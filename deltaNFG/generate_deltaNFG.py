from threading import Thread
import jsonpickle
import json
from deltaNFG.Util.get_commits import *
from deltaNFG.Util.generate_pdg import PDG_Generator
from deltaNFG.Util.git_util import Git_Util
from deltaNFG.deltaNFG import deltaPDG
import os
import networkx as nx


def worker(work, subject_location, id_, temp_loc, extractor_location):
    repository_name = os.path.basename(subject_location)
    method_fuzziness = 100
    node_fuzziness = 100

    git_handler = Git_Util(temp_dir=temp_loc)
    with git_handler as gh:
        v1 = gh.move_git_repo_to_tmp(subject_location)
        v2 = gh.move_git_repo_to_tmp(subject_location)
        os.makedirs('./temp/%d' % id_, exist_ok=True)
        v1_pdg_generator = PDG_Generator(extractor_location=extractor_location,
                                         repository_location=v1,
                                         target_filename='before_pdg.dot',
                                         target_location='./temp/%d' % id_)
        v2_pdg_generator = PDG_Generator(extractor_location=extractor_location,
                                         repository_location=v2,
                                         target_filename='after_pdg.dot',
                                         target_location='./temp/%d' % id_)
        for commit in work:
            print('Working on commit: %s' % str(commit))
            gh.set_git_to_rev(commit + '^', v1)
            gh.set_git_to_rev(commit, v2)
            gh.cherry_pick_on_top(commit, v2)

            changes = gh.process_diff_between_commits(commit + '^', commit, v2)
            files_touched = {filename for _, filename, _, _, _ in changes if
                             os.path.basename(filename).split('.')[-1] == 'cs'}

            for filename in files_touched:
                output_path = './data/delta-NFGs/%s/%s/%s.dot' % (
                    repository_name, commit, os.path.basename(filename))
                try:
                    with open(output_path) as f:
                        print('Skipping %s as it exits' % output_path)
                        f.read()
                except FileNotFoundError:
                    v1_pdg_generator(filename)
                    v2_pdg_generator(filename)
                    delta_gen = deltaPDG('./temp/%d/before_pdg.dot' % id_, m_fuzziness=method_fuzziness,
                                         n_fuzziness=node_fuzziness)
                    delta_pdg = delta_gen('./temp/%d/after_pdg.dot' % id_,
                                          [ch for ch in changes if ch[1] == filename])
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    nx.drawing.nx_pydot.write_dot(delta_pdg, output_path)


def NFG(repository_name):
    json_location = "./data/history/{}/commits.json".format(repository_name)
    subject_location = "./subjects/{}".format(repository_name)
    temp_loc = "./temp"
    id_ = 0
    n_workers = 1
    extractor_location = "./extractor/Release/PdgExtractor.exe"

    try:
        with open(json_location) as f:
            list_to_tangle = jsonpickle.decode(f.read())
    except FileNotFoundError:
        list_to_tangle = get_commits('./subjects/%s' % repository_name, './temp')
        os.mkdir("./data/history/{}".format(repository_name))
        with open("./data/history/{}/commits.json".format(repository_name), 'w') as f:
            f.write(json.dumps(list_to_tangle))

    chunck_size = int(len(list_to_tangle) / n_workers)
    list_to_tangle = [list_to_tangle[i:i + chunck_size] for i in range(0, len(list_to_tangle), chunck_size)]
    threads = []
    for work in list_to_tangle:
        t = Thread(target=worker, args=(work, subject_location, id_, temp_loc, extractor_location))
        id_ += 1
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    repository_name = "Example"
    NFG(repository_name)
