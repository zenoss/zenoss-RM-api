[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true} #turn off cert validation
$URL = "https://zenoss5.sma-dev01.zenoss.lab"
#$creds = get-credential # get your password
#$user = $creds.GetNetworkCredential().UserName
#$pass = $creds.GetNetworkCredential().Password
$user="zenoss"
$pass="Zenny12355"

$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $user,$pass)))

#$data = @ {limit=500} ConvertTo-Json -Compress
$data = $NULL | ConvertTo-Json -Compress
#$json =
$json = @{action="DeviceRouter";method="getDevices";data=$data;tid='1'} | ConvertTo-Json -Compress

$output = Invoke-RestMethod `
-ContentType "application/json" `
-uri "$URL/zport/dmd/device_router" `
-Headers @{Authorization=("Basic {0}" -f $base64AuthInfo)} <#-UseDefaultCredentials#> `
-Method POST -body $json

#Write-Output $output | ConvertTo-Json

Write-Output $output.title