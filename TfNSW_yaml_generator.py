__author__ = 'camrossi'
import yaml
import argparse

def load_yaml_file(path):
    f = open(path, 'r')
    model = yaml.load(f)
    f.close()
    return model


# parser = argparse.ArgumentParser()
# parser.add_argument("-f")
# args = parser.parse_args()
#
# print load_yaml_file(args.f)


args = {        'tenant': input_raw_input("Tenant Name", required=True),
                'application': input_raw_input("Application Name", required=True),
                'epg': input_raw_input("epg Name", required=True),
                'switche(s)': input_raw_input("Switche(s) ID(s)", required=True),
                'interface_type': input_raw_input("Interface Mode", required=True),
                'interface_selector_name': input_raw_input("Interface Selector Name", required=True),
                'epg': input_raw_input("epg Name", required=True),
                'epg': input_raw_input("epg Name", required=True),

            }





