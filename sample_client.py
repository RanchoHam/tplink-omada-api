#!/usr/bin/env python3
"""Cmd line to work out the API."""

import asyncio
import sys
from pprint import pprint
from src.tplink_omada_client.omadaclient import OmadaClient
from src.tplink_omada_client.omadasiteclient import AccessPointPortSettings


async def do_the_magic(url: str, username: str, password: str):
    """Not a real test client."""

    async with OmadaClient(url, username, password, verify_ssl=False) as client:
        print(f"Found Omada Controller: {await client.get_controller_name()}")

        sites = await client.get_sites()
        print(f"Found {len(sites)} sites")
        for site in sites:
            print(f"Connecting to {site.name}")

            site_client = await client.get_site_client(site)

            devices = await site_client.get_devices()

            print(f"Found {len(devices)} Omada devices in site {site.name}.")
            print(f"    {len([d for d in devices if d.type == 'ap'])} Access Points.")
            print(f"    {len([d for d in devices if d.type == 'switch'])} Switches.")
            print(f"    {len([d for d in devices if d.type == 'gateway'])} Routers.")

            for firmware_details in [await site_client.get_firmware_details(d) for d in devices if d.need_upgrade]:
                print("Available firmware upgrade:")
                pprint(vars(firmware_details))

            access_points = [await site_client.get_access_point(a) for a in devices if a.type == "ap"]
            for access_point in access_points:
                print(f"Access Point: {access_point.name}")
                if access_point.name == "Office":
                    port_status = await site_client.update_access_point_port(
                        access_point, "ETH3", AccessPointPortSettings(enable_poe=True)
                    )
                    pprint(vars(port_status))
                    port_status = await site_client.update_access_point_port(
                        access_point, "ETH3", AccessPointPortSettings(enable_poe=False)
                    )
                    pprint(vars(port_status))

            # Get full info of all switches
            switches = [await site_client.get_switch(s) for s in devices if s.type == "switch"]
            for switch in switches:
                print(f"Switch: {switch.name}")
                ports = await site_client.get_switch_ports(switch)
                for port in ports:
                    print(f"{port.name}, {port.profile_name}, {port.poe_mode}")

            router = await site_client.get_gateway()
            print(f"{router.name}")

        print("Done.")


def main():
    """Basic sample test client."""
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: client <omada url> [username] [password]")
        return

    omadaurl = sys.argv[1]
    username = "admin" if len(sys.argv) < 3 else sys.argv[2]
    password = "admin" if len(sys.argv) < 4 else sys.argv[3]

    asyncio.run(do_the_magic(omadaurl, username, password))


main()
