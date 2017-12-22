<?php
$sock = stream_socket_client('unix:///tmp/git2deploy.sock', $errno, $errstr);
if (!$sock)
{
    echo $errstr;
    die("Unable to write to socket");
}
fwrite($sock, $_GET["repo"] . " " . $_SERVER["HTTP_X_HUB_SIGNATURE"] . " " . file_get_contents("php://input") . "\r\n");

fclose($sock);

?>
