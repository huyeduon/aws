#!/bin/bash


# Expects 4 para 
# Para 1 : Pod start number
# Para 2 : Pod end number
# Para 3 : priority region - Which region to delete first
# Para 4 : csv file with subscription info  ( Static )
# ./aws-destroy-pod.sh -b 0 -s /.secrets/class-sub-infra.csv
function destroy_region () {

        Tenant=$1
        Key=$2
        Secret=$3
        region=$4

        printf "\n$FUNCNAME : ........\n" 

        wipe_region $Tenant $Key $Secret $region 

        clean_region $Tenant $Key $Secret $region  
  
        release_vpc_ip $Tenant $Key $Secret $region 
}

function wipe_region () {
# $1 - File containing Tenant name, key secret
# $2 - Region to work on
        Tenant=$1
        Key=$2
        Secret=$3
        region=$4


        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : Wiping out $Tenant @ $region"

        #              wipe_user
        #
        # Search all instances define in $1
        #        
        terminate_instance $Key $Secret $region 


        if [[ $Tenant == *"infra"* ]]; then
                #while read VPC
                #do
                #        clean_subnet  $Key $Secret $region   $VPC              
                #        clean_rt $Key $Secret $region   $VPC
                #done < <(aws ec2 describe-vpcs --filters 'Name=isDefault,Values=false' | jq '.Vpcs[].VpcId' | jq -r)

                delete_tgw_peer_connection  $Key $Secret $region
                
                delete_all_share $Key $Secret $region
                
                delete_tgw_route_association $Key $Secret $region

        fi    



        #
        # Search all tgw atatchments define in $1
        #   

        delete_tgw_attachments $Key $Secret $region 
                
        #
        # Search all tgw if Tenant is non-infra define in $1
        # 

        if [[ $Tenant == *"infra"* ]]; then
                
                printf "\n$FUNCNAME : Deleting TGWs from $Tenant @ $region"
                delete_tgw $Key $Secret $region 
        else
                printf "\n$FUNCNAME : Deleting All TGWs Peer Connections from $Tenant @ $region"       
        fi                 
        
}

function clean_region() {


        Tenant=$1
        Key=$2
        Secret=$3
        region=$4

        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region
        
        printf "\n$FUNCNAME : All instances in $Tenant at $region terminated..\n"  
        
        Wait_instance_terminate $Key $Secret $region                

        if [[ $Tenant == *"infra"* ]]
        then
                 printf "\n$FUNCNAME: All tgw in $Tenant at $region terminated..\n"  
                 Wait_tgw_instance_terminate  $Key $Secret $region  
        fi 


                while read VPC
                do
                                        #
                        # Search for all igw in this VPC
                        #                       

                        clean_network_Interfaces  $Key $Secret $region $VPC

                        #
                        # Search for all igw in this VPC
                        #
                        clean_igw $Key $Secret $region   $VPC 
                        #
                        # Remove all subnets
                        #
                        clean_subnet  $Key $Secret $region   $VPC
                              
                        clean_rt $Key $Secret $region   $VPC

                        clean_SG $Key $Secret $region   $VPC

                        clean_stack $Tenant $Key $Secret $region   
   

                        #
                        # Delete the vPC regareless 
                        #                        
                        vpc_state="$(aws ec2 describe-vpcs --query "Vpcs[?VpcId=='$VPC']" | jq '.[].State' | jq -r)"

                        if [ "$vpc_state" == "available" ] ; then
                                printf "\n$FUNCNAME : Deleting $VPC\n"
                                aws ec2 delete-vpc --vpc-id $VPC
                        fi

                done < <(aws ec2 describe-vpcs --filters 'Name=isDefault,Values=false' | jq '.Vpcs[].VpcId' | jq -r)
    
}

function wipe_user() {

        export AWS_ACCESS_KEY_ID=$1
        export AWS_SECRET_ACCESS_KEY=$2
        Key=$1

        while read user 
        do
                case $user in
                admin)
                        printf "\n$FUNCNAME : $user user\n"
                        printf "\n$FUNCNAME : Remove API Key other than my key\n"
                        while read api_key
                        do
                                if [ $api_key == $Key ] ; then
                                        printf "\n$FUNCNAME : $api_key = $Key\n"
                                else
                                        printf "\n$FUNCNAME : $api_key is not $Key"
                                        printf "\n$FUNCNAME : Removing backdoor key...\n"
                                        printf "\n$FUNCNAME : Deleteing Key $api_key for $user\n"
                                        aws iam delete-access-key --user-name $user --access-key-id $api_key
                                fi
                        done < <(aws iam list-access-keys --user-name $user | jq '.AccessKeyMetadata[].AccessKeyId' | jq -r)
                                        
                        ;;
                cAPIC-admin)
                        printf "\n$FUNCNAME : $user user\n"
                        printf "\n$FUNCNAME : Remove API Key\n"
                        while read api_key
                        do
                                aws iam delete-access-key --user-name $user --access-key-id $api_key
                                printf "\n$FUNCNAME : Deleteing Key $api_key for $user\n"
                        done < <(aws iam list-access-keys --user-name $user | jq '.AccessKeyMetadata[].AccessKeyId' | jq -r)
                        ;;
                                        
                *)
                printf "\n$FUNCNAME : Deleting user $user\n"

                #
                #detach user from all group
                #
                        while read group
                        do
                                printf "\n$FUNCNAME : Detach $user from $group\n"
                                aws iam remove-user-from-group --group-name $group --user-name $user
                        done < <(aws iam list-groups-for-user --user-name $user | jq '.Groups[].GroupName' | jq -r)

                                                
                
                        #
                        # Detach all polcies with this user
                        #
                        while read user_policy
                        do
                                printf "\n$FUNCNAME : Detach $user from $user_policy\n"
                                aws iam detach-user-policy --policy-arn $user_policy --user-name $user
                        done < <(aws iam list-attached-user-policies --user-name $user | jq '.AttachedPolicies[].PolicyArn' | jq '-r')
                                        
                        #
                        # Delete any login profile with this user
                        #

                        aws iam get-login-profile --user-name $user > /dev/null
                                         
                        if  [ $? -ne 0 ];  then
                                printf  "\n$FUNCNAME : $user has no login profile"
                        else
                                printf  "\n$FUNCNAME : Deleting $user login profile"
                                aws iam delete-login-profile --user-name $user
                        fi
                                        
                        while read api_key
                        do
                                aws iam delete-access-key --user-name $user --access-key-id $api_key
                                printf "\n$FUNCNAME : Deleteing Key $api_key for $user\n"
                        done < <(aws iam list-access-keys --user-name $user | jq '.AccessKeyMetadata[].AccessKeyId' | jq -r)
                                        
                        aws iam delete-user --user-name $user;;
                esac

        done < <(aws iam list-users | jq '.Users[].UserName' | jq -r)

        # 
        # Delete all ssh keys creates
        #
        while read keyname
        do
                printf "\nDeleting Key : $keyname from tenant $name\n"
                aws ec2 delete-key-pair --key-name $keyname
        done < <(aws ec2 describe-key-pairs | jq -r '.KeyPairs[].KeyName')
}


function clean_network_Interfaces() {

        Key=$1
        Secret=$2
        region=$3
        VPC=$4


        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"
        #
        # Remove All Network Interfaces
        #
        while read nic
        do
                printf "\n$FUNCNAME : Deleting NIC $nic"
                aws ec2  delete-network-interface --network-interface-id $nic
        done < <(aws ec2 describe-network-interfaces --filters Name=vpc-id,Values=$VPC | jq '.NetworkInterfaces[].NetworkInterfaceId' | jq -r)
}

function clean_igw() {
        
        Key=$1
        Secret=$2
        region=$3
        VPC=$4

        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"

        while read igw
        do
                printf "\n$FUNCNAME : Deleting igw $igw from $region\n"
                aws ec2 detach-internet-gateway --internet-gateway-id $igw --vpc-id $VPC
                        
                aws ec2 delete-internet-gateway --internet-gateway-id $igw
                        
        done < <(aws ec2 describe-internet-gateways --filters 'Name=attachment.vpc-id,Values='$VPC'' | jq '.InternetGateways[].InternetGatewayId' | jq -r)

}

function clean_subnet() {

        Key=$1
        Secret=$2
        region=$3
        VPC=$4


        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"

        while read subnet
        do
               printf "\n$FUNCNAME : Deleting subnet $subnet from from $VPC\n"
               aws ec2 delete-subnet --subnet-id $subnet
        done < <(aws ec2 describe-subnets --filters 'Name=vpc-id,Values='$VPC'' | jq '.Subnets[].SubnetId' | jq -r)   

}

function clean_rt() {


        Key=$1
        Secret=$2
        region=$3
        VPC=$4


        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"
        main_rt="$(aws ec2 describe-route-tables --filters  Name=vpc-id,Values=$VPC | jq '.RouteTables[].Associations[].RouteTableId' | jq -r)"
        while read rt
        do
                if [ $rt != $main_rt ]
                then
                        printf "\n$FUNCNAME : $rt is not main route table.. deleting\n"
                        aws ec2 delete-route-table --route-table-id $rt
                fi
        done < <(aws ec2 describe-route-tables --filters  Name=vpc-id,Values=$VPC | jq '.RouteTables[].RouteTableId' | jq -r)
}



function clean_SG() {   


        Key=$1
        Secret=$2
        region=$3
        VPC=$4


        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"
        # 
        # Get a list of non default vpc SGACL
        #       
        # full_list="$(aws ec2 describe-security-groups --filters  Name=vpc-id,Values=$1 --query 'SecurityGroups[?!contains(Description,`default`) == `true`][GroupId]' | jq '.[][0]' | jq -r| sort | uniq)"
        # 
        # Get a list of SG ACL beinf reference
        #

        while read sg_group
        do

                printf "\n$FUNCNAME : Deleting $sg_group\n"
                json="$(aws ec2 describe-security-groups --group-id $sg_group --query "SecurityGroups[0].IpPermissions" | jq  '.[] |  select (.IpProtocol != null)')"            
                
                if [[ ${json[@]} ]]; then
                        # This SG is not null, remove all permissions
                        json="$(aws ec2 describe-security-groups --group-id $sg_group --query "SecurityGroups[0].IpPermissions")"
                        aws ec2 revoke-security-group-ingress --cli-input-json "{\"GroupId\": \"$sg_group\", \"IpPermissions\": $json}" 2>/dev/null
                fi

                json=`aws ec2 describe-security-groups --group-id $sg_group --query "SecurityGroups[0].IpPermissionsEgress"| jq  '.[] |  select (.IpProtocol != null) '`
                 if [[ ${json[@]} ]]; then
                        # This SG is not null, remove all permissions
                        json="$(aws ec2 describe-security-groups --group-id $sg_group --query "SecurityGroups[0].IpPermissionsEgress")"
                        aws ec2 revoke-security-group-egress --cli-input-json "{\"GroupId\": \"$sg_group\", \"IpPermissions\": $json}" 2>/dev/null
                fi
                
                aws ec2 delete-security-group --group-id $sg_group 2>/dev/null
        done < <(aws ec2 describe-security-groups --filters  Name=vpc-id,Values=$VPC --query 'SecurityGroups[?!contains(GroupName,`default`) == `true`]' | jq -r '.[].GroupId')

        while read sg_group
        do      
                aws ec2 delete-security-group --group-id $sg_group 2>/dev/null
        done < <(aws ec2 describe-security-groups --filters  Name=vpc-id,Values=$VPC --query 'SecurityGroups[?!contains(GroupName,`default`) == `true`]' | jq -r '.[].GroupId')

 }

function clean_stack() {


        Key=$2
        Secret=$3
        region=$4
        Tenant=$1


        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"
        IFS=","
        while read stack stack_status
        do
                if [ -z $stack ] ; then
                        printf "\n$FUNCNAME : No more stacks in $Tenant\n"
                else
                        printf "\n$FUNCNAME : Found $stack in $stack_status..\n"
                        printf "\n$FUNCNAME : Deleting $stack\n"
                        aws cloudformation delete-stack --stack-name $stack

                        printf "\n$FUNCNAME : Waiting for $stack to be deleted \n"

                        IFS=","
                        while :;
                        do
                                #read this_stack this_stack_status < <(aws cloudformation list-stacks | jq '.StackSummaries | map([.StackName,.StackStatus]| join(", "))' | tr -d '" []' | sed 's/,$/\n/' | sed '/^[[:space:]]*$/d')
                                read  this_stack this_stack_status < <(aws cloudformation list-stacks --query 'StackSummaries[?contains(StackName,`'$stack'`) == `true`]'  |  jq -r '.[] | [ .StackName, .StackStatus ] | @tsv' | tr -s '\t' ',')

                                if [ $this_stack = $stack -a $this_stack_status = "DELETE_IN_PROGRESS" ]; then
                                        printf "\n$FUNCNAME : $stack stack status = $this_stack_status"
                                        sleep 5
                                else
                                        printf "\n$FUNCNAME : $stack Deleted"
                                        break
                                fi
                                        
                        done 
                fi
        done < <(aws cloudformation list-stacks --query 'StackSummaries[?contains(StackStatus,`DELETE`) == `false`]' | jq -r '.[] | [ .StackName, .StackStatus ] | @tsv' | tr -s '\t' ',')

}

function terminate_instance() {

        Key=$1
        Secret=$2
        region=$3
        VPC=$4


        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"
        
        #
        # Read and Delete all Instances
        #
        while read instance_id instance_state
        do
                printf "\nFound $instance_id is $instance_state state\n"
                        
                if [ "$instance_state" != "terminated" ] ; then
                        printf "\nFound $Tenant @ $AccountID Instance $instance_id in $instance_state at $region\n"
                        aws ec2 terminate-instances --instance-id $instance_id
                fi

        done < <(aws ec2 describe-instances --query 'Reservations[].Instances[].[InstanceId,State.Name]' | tr -d '" []' | sed 's/^,//;N;s/\n//' | sed '/^[[:space:]]*$/d')   
}  

function Wait_instance_terminate() {

        #
        # Wait for Instances  to be removed
        #
        
        Key=$1
        Secret=$2
        region=$3



        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"

        #
        # Previous steps already terminar all instances..
        # Wait for instances to be deleted
        #

        printf "\n@$FUNCNAME "
        while read instance_id instance_state
        do
                        
                if [ "$instance_state" == "terminated" ]; then
                        printf "\n$FUNCNAME : $instance_id already terminated..\n"
                        continue
                fi
                        
                printf "\n$FUNCNAME : Waiting for $instance_id to terminate\n"
                while :;
                do
                        instance_state="$(aws ec2 describe-instances --instance-id  $instance_id| jq  '.Reservations[].Instances[].State.Name'  | tr -d '"')"
                                        
                        if [ "$instance_state" == "terminated" ]; then
                                printf "\n$FUNCNAME :Instance $instance_id terminated"
                                break
                        fi
                        printf "."
                        sleep 1
                done
                        

        done < <(aws ec2 describe-instances --query 'Reservations[].Instances[].[InstanceId,State.Name]' | tr -d '" []' | sed 's/^,//;N;s/\n//' | sed '/^[[:space:]]*$/d')


}

function wait_for_tgw_delele() {

        Key=$1
        Secret=$2
        region=$3
        tgw_conn_peer=$4

        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region
 
        
        while :;
        do
                read tgw_conn_peer_state  < <(aws ec2 delete-transit-gateway-connect-peer --transit-gateway-connect-peer-id $tgw_conn_peer  | jq -r '.TransitGatewayConnectPeer.State')
                                
                if [ $tgw_conn_peer_state  = "deleting" ]; then
                        printf "\n$FUNCNAME : TGW Conn Peer $tgw_conn_peer  status = $tgw_conn_peer_state"
                        sleep 5
                else
                        printf "\n$FUNCNAME : $tgw_conn_peer Deleted"
                        break
                fi                                        
        done 

        jq '.TransitGatewayConnectPeer.State'

}

function delete_tgw_peer_connection() {

        Key=$1
        Secret=$2
        region=$3

        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : export AWS_DEFAULT_REGION=$region"
        printf "\n$FUNCNAME : export AWS_ACCESS_KEY_ID=$Key"
        printf "\n$FUNCNAME : export AWS_SECRET_ACCESS_KEY=$Secret"
 
        printf "\n$FUNCNAME : Retriving TGW Peer Connection from region  $region\n"


        while read tgw_conn_peer
        do
                printf "\n$FUNCNAME : Deleting TGW Connection Peer $tgw_conn_peer from region  $region\n"
                aws ec2 delete-transit-gateway-connect-peer --transit-gateway-connect-peer-id $tgw_conn_peer
        done < <(aws ec2 describe-transit-gateway-connect-peers  | jq -r '.TransitGatewayConnectPeers[].TransitGatewayConnectPeerId')

        while read tgw_conn_peer
        do
                printf "\n$FUNCNAME : Waiting TGW Connection Peer to be deleted $tgw_conn_peer from region  $region\n"
                wait_for_tgw_delele $Key $Secret $region $tgw_conn_peer &
        done < <(aws ec2 describe-transit-gateway-connect-peers  | jq -r '.TransitGatewayConnectPeers[].TransitGatewayConnectPeerId')
        wait

}

function delete_tgw_route_association() {

        Key=$1
        Secret=$2
        region=$3

        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : export AWS_DEFAULT_REGION=$region"
        printf "\n$FUNCNAME : export AWS_ACCESS_KEY_ID=$Key"
        printf "\n$FUNCNAME : export AWS_SECRET_ACCESS_KEY=$Secret"
 
        printf "\n$FUNCNAME : Retriving TGW Peer Connection from region  $region\n"



        IFS=","
        while read tgw_route_table tgw_id
        do
                        printf "\n$FUNCNAME : Deleting $tgw_route_table"

                        IFS=","
                        while read tgw_attachment_id  attachment_type
                        do
                                printf "\n$FUNCNAME : route table association $tgw_route_table $tgw_attachment_id  "
                                aws ec2  disable-transit-gateway-route-table-propagation --transit-gateway-route-table-id  $tgw_route_table --transit-gateway-attachment-id $tgw_attachment_id 
                                aws ec2  disassociate-transit-gateway-route-table --transit-gateway-route-table-id  $tgw_route_table --transit-gateway-attachment-id $tgw_attachment_id 
                                
                                if [[ $attachment_type == "vpc" ]];then
                                # Delete all vpc attachment
                                        aws ec2 delete-transit-gateway-vpc-attachment --transit-gateway-attachment-id $tgw_attachment_id 2>/dev/null
                                else
                                # Delete all connect attachment
                                        aws ec2 delete-transit-gateway-connect --transit-gateway-attachment-id $tgw_attachment_id 2>/dev/null
                                fi
                                

                        done < <(aws ec2  get-transit-gateway-route-table-associations --transit-gateway-route-table-id $tgw_route_table  | jq -r '.Associations[] | [ .TransitGatewayAttachmentId, .ResourceType ] | @tsv' | tr -s '\t' ',' )
                        
                        aws ec2 delete-transit-gateway-route-table --transit-gateway-route-table-id  $tgw_route_table      
        done < <(aws ec2 describe-transit-gateway-route-tables |  jq -r '.TransitGatewayRouteTables[] | [ .TransitGatewayRouteTableId, .TransitGatewayId ] | @tsv' | tr -s ' \t' ',')
}

function Wait_tgw_instance_terminate() {
        #
        # Wait for TGW  to be removed
        #
        
        Key=$1
        Secret=$2
        region=$3

        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region                       
        

        printf "\n@$FUNCNAME....... "

        while read tgw tgw_state
        do
        printf "\n$FUNCNAME : Waiting for TGW $tgw to be deleted \n"

        if [ "$tgw_state" == "deleted" ]; then
                printf "\n$FUNCNAME : $tgw already deleted..\n"
                continue
        fi

                while read tgw_state
                do
                #tgw_state="$(aws ec2 describe-transit-gateways  --transit-gateway-id $tgw| jq '.TransitGateways[].State' | jq -r)"
                        if [ $tgw_state = "deleted" ]; then
                                printf "\n$FUNCNAME : \n"
                                break
                        fi
                
                        aws ec2 delete-transit-gateway --transit-gateway-id  $tgw 2>/dev/null                
                        printf "."
                        sleep 1
                done < <(aws ec2 describe-transit-gateways  --transit-gateway-id $tgw| jq '.TransitGateways[].State' | jq -r)
                                
        done < <(aws ec2 describe-transit-gateways | jq '.TransitGateways | map([.TransitGatewayId,.State] | join(", "))' | tr -d '" []' | sed 's/,$/\n/' | sed '/^[[:space:]]*$/d')

}

function delete_tgw_attachments() {
        
        Key=$1
        Secret=$2
        region=$3

        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"


                #
                # Search for all non default VPC
                #

                while read VPC
                do
                        printf "\n$FUNCNAME :  Checking $VPC\n"

                        # Remove TGW Attachments and TGW of Resource Type = Connect
                        #
                        IFS=","
                        while read tgw_attachment  tgw
                        do
                                printf "\n$FUNCNAME : Deleteing TGW Connect Attachment $tgw_attachment\n"

                                # Remove all peer first 

                                while read tgw_connect_peer
                                do
                                        printf "\n$FUNCNAME : Removing $tgw_connect_peer from $tgw_attachment\n"
                                        aws ec2 delete-transit-gateway-connect-peer --transit-gateway-connect-peer-id $tgw_connect_peer
                                done < <(aws ec2 describe-transit-gateway-connect-peers --filters Name=transit-gateway-attachment-id,Values=$tgw_attachment | jq '.TransitGatewayConnectPeers | map([.TransitGatewayConnectPeerId])'| tr -d '" [],' | sed '/^[[:space:]]*$/d')

                                aws ec2 delete-transit-gateway-connect --transit-gateway-attachment-id $tgw_attachment 2>/dev/null
                        done < <(aws ec2 describe-transit-gateway-connects | jq '.TransitGatewayConnects | map([.TransitGatewayAttachmentId,.TransitGatewayId] | join(", "))' | tr -d '" []' | sed 's/,$/\n/' | sed '/^[[:space:]]*$/d')
                        

                        while read tgw_attachment  tgw_attachment_state
                        do
                                printf "\n$FUNCNAME : Waiting for TGW Attachement - Connect $tgw_attachment to be deleted \n"
                                if [ "$tgw_attachment_state" == "deleted" ]; then
                                        printf "\n$FUNCNAME : $tgw_attachment already deleted..\n"
                                        continue
                                fi

                                while :;
                                do
                                        tgw_attachment_state="$(aws ec2 describe-transit-gateway-attachments --filters Name=resource-type,Values=connect Name=transit-gateway-attachment-id,Values=$tgw_attachment | jq '.TransitGatewayAttachments[].State' | jq -r)"
                                        if [ $tgw_attachment_state = "deleted" ]; then
                                                printf "\n$FUNCNAME : "
                                                break
                                        fi
                                        aws ec2 delete-transit-gateway-connect --transit-gateway-attachment-id $tgw_attachment 2>/dev/null
                                        printf "."
                                        sleep 1
                                done

                        done < <(aws ec2 describe-transit-gateway-connects | jq '.TransitGatewayConnects | map([.TransitGatewayAttachmentId,.TransitGatewayId] | join(", "))' | tr -d '" []' | sed 's/,$/\n/' | sed '/^[[:space:]]*$/d')
                        
                        #

                        #
                        # Remove TGW Attachments and TGW of Resource Type = VPC
                        #
                        IFS=","
                        while read tgw_attachment  tgw
                        do
                                printf "\n$FUNCNAME : Deleteing TGW Attchment $tgw_attachment\n"
                                aws ec2 delete-transit-gateway-vpc-attachment --transit-gateway-attachment-id $tgw_attachment 2>/dev/null
                        done < <(aws ec2 describe-transit-gateway-attachments --filters Name=resource-id,Values=$VPC Name=state,Values=available | jq '.TransitGatewayAttachments | map([.TransitGatewayAttachmentId,.TransitGatewayId] | join(", "))' | tr -d '" []' | sed 's/,$/\n/' | sed '/^[[:space:]]*$/d')
                        #
                        # Wait for TGW Attcahment to be removed
                        #
                        while read tgw_attachment  tgw_attachment_state
                        do
                                printf "\n$FUNCNAME : Waiting for TGW Attachement $tgw_attachment to be deleted \n"
                                if [ "$tgw_attachment_state" == "deleted" ]; then
                                        printf "\n$FUNCNAME : $tgw_attachment already deleted..\n"
                                        continue
                                fi

                                while read tgw_attachment_state
                                do
                                        #tgw_attachment_state="$(aws ec2 describe-transit-gateway-attachments --filters Name=resource-id,Values=$VPC Name=transit-gateway-attachment-id,Values=$tgw_attachment | jq '.TransitGatewayAttachments[].State' | jq -r)"
                                        if [ $tgw_attachment_state = "deleted" ]; then
                                                printf "\n$FUNCNAME : "
                                                break
                                        fi
                                        aws ec2 delete-transit-gateway-vpc-attachment --transit-gateway-attachment-id $tgw_attachment 2>/dev/null
                                        printf "."
                                        sleep 1
                                done < <(aws ec2 describe-transit-gateway-attachments --filters Name=resource-id,Values=$VPC Name=transit-gateway-attachment-id,Values=$tgw_attachment | jq '.TransitGatewayAttachments[].State' | jq -r)

                        done < <(aws ec2 describe-transit-gateway-attachments --filters Name=resource-id,Values=$VPC  | jq '.TransitGatewayAttachments | map([.TransitGatewayAttachmentId,.State] | join(", "))' | tr -d '" []' | sed 's/,$/\n/' | sed '/^[[:space:]]*$/d')
                #
                done < <(aws ec2 describe-vpcs --filters 'Name=isDefault,Values=false' | jq '.Vpcs[].VpcId' | jq -r)

}

function delete_all_share() {

        Key=$1
        Secret=$2
        region=$3

        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"
        printf "\n$FUNCNAME : Retriving TGW from region  $region\n"

        while read arn resource_arn
        do
                printf "\n$FUNCNAME : \t\tDeleting resource_arn : $resource_arn is invalid \n"
                aws ram delete-resource-share --resource-share-arn $resource_arn    
        done < <(aws ram list-resources --resource-owner SELF | jq -r '.resources[] | [ .arn, .resourceShareArn  ] | @tsv' | tr -s ' \t' ',')


}



function delete_tgw() {

        Key=$1
        Secret=$2
        region=$3

        export AWS_ACCESS_KEY_ID=$Key
        export AWS_SECRET_ACCESS_KEY=$Secret       
        export AWS_DEFAULT_REGION=$region

        printf "\n$FUNCNAME : region = $region"
        printf "\n$FUNCNAME : Retriving TGW from region  $region\n"

        while read arn resource_arn
        do
                printf "\n$FUNCNAME : \t\tDeleting resource_arn : $resource_arn is invalid \n"
                aws ram delete-resource-share --resource-share-arn $resource_arn    
        done < <(aws ram list-resources --resource-owner SELF | jq -r '.resources[] | [ .arn, .resourceShareArn  ] | @tsv' | tr -s ' \t' ',')

        
 
        while read tgw
        do
                printf "\n$FUNCNAME : Deleteing TGW $tgw\n"
                aws ec2 delete-transit-gateway --transit-gateway-id  $tgw 2>/dev/null

                while read tgw_state
                do
                        if [ $tgw_state = "deleted" ]; then
                                printf "\n$FUNCNAME : \n"
                                break
                        fi
                
                        aws ec2 delete-transit-gateway --transit-gateway-id  $tgw 2>/dev/null                
                        printf "."
                        sleep 1
                done < <(aws ec2 describe-transit-gateways  --transit-gateway-id $tgw| jq '.TransitGateways[].State' | jq -r)
                

        done < <(aws ec2 describe-transit-gateways | jq '.TransitGateways[].TransitGatewayId' | jq -r)

}

function release_vpc_ip() {

    Tenant=$1
    Key=$2
    Secret=$3
    region=$4

    export AWS_ACCESS_KEY_ID=$Key
    export AWS_SECRET_ACCESS_KEY=$Secret
    export AWS_DEFAULT_REGION=$region
    printf "\n$FUNCNAME : region = $region"
    
    IFS="," 
    while read ip allocation
    do
        printf "\n$FUNCNAME : releasing $ip allocation-id $allocation user for tenant $name region $region\n"
        aws ec2 release-address --allocation-id $allocation
    done < <(aws ec2   describe-addresses | jq -r '.Addresses[] | [.PublicIp, .AllocationId] | @tsv' | tr -s '\t' ',')

}

function help_msg () {
   
    printf "\n$0 -s <start Pod> -e <end pod> -r region -s <subs-list>\n"
    printf "\n\t\t-b Begin Pod Number, must be lower than End Pod Number, if undefined, set to End \n"
    printf "\n\t\t-e End  Pod Number, msut be greater thab Begin Pod Number, if undefined, set to Begin \n"
    printf "\n\t\t-r AWS region to create test-instance\n"
    printf "\n\t\t-s csv file with subscription data\n"    
    
}

while getopts b:e:s:r: flag;
do
    case $flag in
        b)
            
            if [ "$OPTARG" -eq "$OPTARG" ] 2>/dev/null; 
            then
                start=$OPTARG
                printf "\nStart = $start, OPTIND =  $OPTIND, $#"
                printf "\nvarname = $varname"
                
            else
                help_msg 
                exit 1
            fi

            ;;
        e) 
            end=$OPTARG

            if [ "$OPTARG" -eq "$OPTARG" ] 2>/dev/null; 
            then
                end=$OPTARG
            else
                help_msg 
                exit 1
            fi
            ;;
        s) 

            if [ -f "$OPTARG" ]
            then
                subs_list=$OPTARG
            else
                printf "\n$OPTARG not found\n"
                exit 1 
            fi
            ;;
        r)
            if [ "$OPTARG" ] 2>/dev/null; 
            then
                priority_region=$OPTARG
            else
                help_msg 
                exit 1
            fi
            ;;
        :)
            printf "\nInvalid - parameter \n"
            help_msg
            ;;
        *)
            help_msg 
            exit 1
            ;;
    esac
done


shift $(( OPTIND-1 ))

printf "\nExited Loop \n"

if [ "$start" -eq "$start" -a "$end" -eq "$end" ] 2>/dev/null
then
    printf "\nBoth Start and end defined\n"
elif [ "$start" -eq "$start" ] 2>/dev/null
then
    end=$start
elif [ "$end" -eq "$end" ] 2>/dev/null
then
    start=$end
else
    printf "\nStart and End Not defined\n"
    help_msg 
    exit 1
fi

if [ -z "$subs_list" ]
then
    printf "\nNo Subscription File defined"
    help_msg
    exit 1
fi

if [ "$priority_region" ]
then
    printf "\nCreating key for $priority_region\n"
else
    priority_region="us-east-1"
fi

i=$start

printf "\nStart, Stop, Region, List = $start, $end, $priority_region, $subs_list\n"

while [[ $i -le $end  ]]
do
    if [[ $i -eq 0 ]]
    then
        printf "\nPod $i cannot be deleted. Insufficient priviledge\n"
        exit
    fi    

    if [[ $i -lt 10 ]]
    then
        pod_id="Student0${i}"

    else
        pod_id="Student${i}"
    fi

    printf "\nPriority Region = $priority_region\n"
    printf "\nRemove All  Users "

    IFS="," 
    while read name aws_account aws_key aws_secret azure_role azure_subs
    do
        printf "\n\nRemoving $name, AWS Account  = $aws_account"

        wipe_user $aws_key $aws_secret 

        destroy_region $name $aws_key $aws_secret $priority_region &

        ssh_keyname="${name}-ssh"
        ssh_key_fingerprint="${name}-ssh.fingerprint"
        rm keys/$ssh_keyname.pem
        rm keys/$ssh_key_fingerprint
#        wipe_region $name $aws_key $aws_secret $priority_region 
#
#        clean_region $aws_key $aws_secret $priority_region $name 
#  
#       release_vpc_ip $name $aws_key $aws_secret  $priority_region 
    done < <(grep  $pod_id $subs_list) 

    ((i=i+1))
done

exit 
i=$start
while [[ $i -le $end  ]]
do
    IFS="," 
    while read name aws_account aws_key aws_secret azure_role azure_subs
    do 
        while read region 
        do
                if [ "$region" != "$priority_region" ]
                then
                        destroy_region $name $aws_key $aws_secret $region $
                else
                        printf "\nSkipping $region"                       
                fi   
        done < <(aws ec2 describe-regions | jq '.Regions[].RegionName'| jq -r) 
    done < <(grep  $pod_id $subs_list)
    ((i=i+1))

done