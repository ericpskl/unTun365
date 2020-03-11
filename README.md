# unTun365

unTun365 downloads (directly from Microsoft!) the list of IPv4 and IPv6 networks used to provide Office 365 services. It then converts the IPv4 netblocks into syntax compatible with an OpenVPN server.

Incorporating the generated syntax into an OpenVPN server's config file has the effect of causing connected clients to route Office 365 traffic directly to their default LAN gateway and not across the VPN tunnel.  This increases performance for the end user while significantly reducing load on enterprise networks. 

## Usage

You'll need Python 3 with a few standard libraries (`requests` and `uuid`). These are probably already installed under your distro.

I recommend configuring the script to output to a file called `DEFAULT` placed under the OpenVPN's client configuration directory. This has the advantage of not interacting with OpenVPN server config file directly.  Updates to client configuration files do not require a restart of the OpenVPN server to take effect; client configuration directives are loaded from disk each time a new connection is established.

You can run this out of cron for automatic updates, although in our testing, the data does not change frequently.  Once a week is probably sufficent.

## Sample OpenVPN syntax

In your OpenVPN server config file, establish a location for the client configuration files:

`client-config-dir /etc/openvpn/ccd`

We also recommend using the following syntax, which will push `0.0.0.0/1` and `128.0.0.0/1` routes to clients, which is
better a second default gateway route of `0.0.0.0/0`

`push "redirect-gateway def1"`

## Permissions

Don't run this as root! Configure an appropriate user account and assign appropriate write permissions to the `DEFAULT` file.

## Testing

From a connected OpenVPN client, check the routing table to confirm that the downloaded routes have been installed.  Under Windows, the output of the `show route` command should have about 200 additional routes loaded with the next-hop pointing to the client's local default gateway.

![Office 365 Routes on a connected Win10 Client](https://raw.githubusercontent.com/ericpskl/unTun365/master/routes.png)

## Caveats

This was only tested under Linux.  We've also included only the IPv4 routes, as this was written to help one of our international clients who is currently only using IPv4 in their OpenVPN environment.

