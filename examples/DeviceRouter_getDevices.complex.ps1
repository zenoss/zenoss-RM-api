function Html-ToText {
 param([System.String] $html)
 # remove line breaks, replace with spaces
 $html = $html -replace "(`r|`n|`t)", " "
 # write-verbose "removed line breaks: `n`n$html`n"
 # remove invisible content
 @('head', 'style', 'script', 'object', 'embed', 'applet', 'noframes', 'noscript', 'noembed') | % {
  $html = $html -replace "<$_[^>]*?>.*?</$_>", ""
 }
 # write-verbose "removed invisible blocks: `n`n$html`n"
 # Condense extra whitespace
 $html = $html -replace "( )+", " "
 # write-verbose "condensed whitespace: `n`n$html`n"
 # Add line breaks
 @('div','p','blockquote','h[1-9]') | % { $html = $html -replace "</?$_[^>]*?>.*?</$_>", ("`n" + '$0' )} 
 # Add line breaks for self-closing tags
 @('div','p','blockquote','h[1-9]','br') | % { $html = $html -replace "<$_[^>]*?/>", ('$0' + "`n")} 
 # write-verbose "added line breaks: `n`n$html`n"
 #strip tags 
 $html = $html -replace "<[^>]*?>", ""
 # write-verbose "removed tags: `n`n$html`n"
 # replace common entities
 @( 
  @("&amp;bull;", " * "),
  @("&amp;lsaquo;", "<"),
  @("&amp;rsaquo;", ">"),
  @("&amp;(rsquo|lsquo);", "'"),
  @("&amp;(quot|ldquo|rdquo);", '"'),
  @("&amp;trade;", "(tm)"),
  @("&amp;frasl;", "/"),
  @("&amp;(quot|#34|#034|#x22);", '"'),
  @('&amp;(amp|#38|#038|#x26);', "&amp;"),
  @("&amp;(lt|#60|#060|#x3c);", "<"),
  @("&amp;(gt|#62|#062|#x3e);", ">"),
  @('&amp;(copy|#169);', "(c)"),
  @("&amp;(reg|#174);", "(r)"),
  @("&amp;nbsp;", " "),
  @("&amp;(.{2,6});", "")
 ) | % { $html = $html -replace $_[0], $_[1] }
 # write-verbose "replaced entities: `n`n$html`n"
 return $html
}

function Get-Title { 
    param([string] $data) 
    $title = [regex] '(?<=<title>)([\S\s]*?)(?=</title>)' 
    write-output $title.Match($data).value.trim() 
}

[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true} #turn off cert validation
$URL = "https://zenoss5.sma-dev01.zenoss.lab"
#
$creds = get-credential # get your password
$user = $creds.GetNetworkCredential().UserName
$pass = $creds.GetNetworkCredential().Password
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $user,$pass)))
#
#$data = @ {limit=500} ConvertTo-Json -Compress
$apiDdata = $NULL | ConvertTo-Json -Compress
$json = @{action="DeviceRouter";method="getDevices";data=$apiData;tid='1'} | ConvertTo-Json -Compress
#
$request = [System.Net.WebRequest]::Create("$URL/zport/dmd/device_router")
#$request.KeepAlive = $true
#$request.Pipelined = $true
$request.AllowAutoRedirect = $true
$request.Method = "POST"
$request.ContentType = "application/json"
$request.Headers.Add("Authorization", "Basic " + $base64AuthInfo)
#
$utf8Bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
$request.ContentLength = $utf8Bytes.Length
$postStream = $request.GetRequestStream()
$postStream.Write($utf8Bytes, 0, $utf8Bytes.Length)
$postStream.Dispose()
#
$response = $request.GetResponse()
$requestStream = $response.GetResponseStream()
$readStream = New-Object System.IO.StreamReader $requestStream
$data=$readStream.ReadToEnd()
#
if($response.ContentType -NotMatch "application/json") {
	Write-Output "ERROR: Unknown response"
	Write-Output $response
	exit 1
} elseif ($response.ContentType -match "text/html") {
	$htmlTitle  = Get-Title $data
	$htmlText = Html-ToText $data
	Write-Output "ERROR: HTML returned, page title: $htmlTitle"
	Write-Output $htmlText
	exit 1
}
#
Write-Output $data | ConvertFrom-Json | ConvertTo-Json