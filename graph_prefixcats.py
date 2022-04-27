#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
A small script to produce a version
of a KGX TSV nodefile in which all
categories are replaced with node
prefixes.
'''

import click  #type: ignore

@click.command()
@click.option("--input",
               required=True,
               nargs=1,
               help="""The name of the graph node file to use as input.""")
@click.option("--output",
               required=True,
               nargs=1,
               help="""The name of the file to produce.""")
def run(input, output):

    print(f"Creating prefixcats nodefile in {output}...")

    with open(input, 'r') as node_file:
        header = node_file.readline()
        with open(output, 'w') as outfile:
            outfile.write(header)
            for line in node_file:
                splitline=line.split('\t')
                prefix = ((splitline[0]).split(':'))[0]
                splitline[1] = prefix
                outline = "\t".join(splitline)
                outfile.write(outline)

    print("Complete.")

if __name__ == '__main__':
  run()