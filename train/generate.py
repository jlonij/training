#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# DAC Entity Linker
#
# Copyright (C) 2017 Koninklijke Bibliotheek, National Library of
# the Netherlands
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import json
import sys
import unicodecsv as csv

sys.path.insert(0, '../../dac')
import dac

def generate():
    with open('../users/tve/art.json') as fh:
        data = json.load(fh)

    with open('training.csv', 'w') as fh:
        linker = dac.EntityLinker(debug=True, candidates=True, train=True)

        metadata = ['entity_id', 'cand_id', 'url', 'ne', 'cand_uri']
        label = ['label']

        csv_writer = csv.writer(fh, delimiter='\t', encoding='utf-8')
        csv_writer.writerow(metadata + linker.model.features + label)

        url = None
        url_result = None
        candidate_count = 1

        for i, inst in enumerate(data['instances']):
            print('Reviewing instance ' + str(i) + ': ' +
                inst['ne_string'].encode('utf-8'))

            # Check if instance has been labeled
            if inst['links']:
                if inst['url'] != url:
                    print('Getting result for url: ' + inst['url'])
                    url = inst['url']
                    url_result = linker.link(inst['url'])['linkedNEs']

                result = [r for r in url_result
                    if r['text'] == inst['ne_string']]
                if len(result) != 1:
                    print('No result for: ' + inst['ne_string'])
                    continue
                else:
                    result = result[0]

                # Check if DBpedia canadidates have been retrieved
                if 'candidates' in result:
                    for cand in result['candidates']:

                        row = []

                        # Metadata
                        row.append(str(inst['id']))
                        row.append(str(candidate_count))
                        row.append(inst['url'].encode('utf-8'))
                        row.append(inst['ne_string'].encode('utf-8'))
                        row.append(cand['id'].encode('utf-8'))

                        # Features
                        for f in linker.model.features:
                            value = cand['features'][f]
                            row.append("{0:.3f}".format(float(value)))

                        # Label
                        if cand['id'] in inst['links']:
                            row.append(str(1))
                        else:
                            row.append(str(0))

                        # Exclude name and date conflicts
                        if cand['features']['match_str_conflict'] == 1:
                            continue
                        elif cand['features']['match_txt_date'] == -1:
                            continue
                        else:
                            candidate_count += 1
                            csv_writer.writerow(row)

if __name__ == '__main__':
    generate()