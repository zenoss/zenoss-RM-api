#!/usr/bin/env python
import zenApiLib
import argparse
import json


class ComponentGroups():
    """ComponentGroupRouter base class."""

    def __init__(self):
        self.api = zenApiLib.zenConnector()

    def get_args(self):
        parser = argparse.ArgumentParser(
            """Generate report of component group members.
               @type uid: string
               @param uid: (requried) Unique identifier of the organzier to get devices from
                   Example: "/zport/dmd/ComponentGroups"
            """
            )
        parser.add_argument(
            "--uid",
            type=str,
            required=True,
            help="Unique identifier of the organizer to get devices from.",
            )
        parser.add_argument(
            "--csv",
            action='store_true',
            help="Output as csv.",
        )
        args = parser.parse_args()
        return(args)

    def getComponentGroupMembers(self, uid):
        """Returns members of the provided component group uid.
           @type uid: string
           @param uid: (required) full uid path of the Component Group
           Example: '/zport/dmd/ComponentGroups/foo'.
        """
        self.api.setRouter('ComponentGroupRouter')
        self.uid = uid
        self.incorrect_uid = {
            "Error": "Uid must be equal to or include /zport/dmd/ComponentGroups"
            }
        if '/zport/dmd/ComponentGroups' not in self.uid:
            return(self.incorrect_uid)
        try:
            results = self.api.pagingMethodCall(
                "getComponents",
                sort="name",
                uid=self.uid,
                keys=[
                    "name",
                    "device",
                    "meta_type",
                    "monitored",
                    "productionState",
                    "locking",
                    "uid"],
                start=0,
                limit=100,
                dir="ASC")
        except Exception as ex:
            raise

        if results:
            for res in results:
                return(res)

    def makeCsv(self, results):
        """Prints the json data as a csv."""
        print("name, device, meta_type, monitored, productionState, "
              "locking: updates, locking: deletion, locking: events, uid")
        for res in results['result']['data']:
            print("%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
                res['name'],
                res['device']['name'],
                res['meta_type'],
                res['monitored'],
                res['productionState'],
                res['locking']['updates'],
                res['locking']['deletion'],
                res['locking']['events'],
                res['uid']))


if __name__=='__main__':
    cg = ComponentGroups()
    my_args = cg.get_args()
    if my_args.csv:
        cg.makeCsv(cg.getComponentGroupMembers(my_args.uid))
    else:
        print(json.dumps(cg.getComponentGroupMembers(my_args.uid)))
