import argparse
import matplotlib.pyplot as plt
import numpy as np

from collections import defaultdict

from atm.config import *


def graph_best_so_far(db, datarun_ids=None, n_learners=100):
    lines = []
    dataruns = db.get_dataruns(ignore_pending=True, ignore_complete=False,
                               include_ids=datarun_ids)

    for r in dataruns:
        # generate a list of the "best so far" score after each learner was
        # computed (in chronological order)
        learners = db.get_learners(datarun_id=r.id)[:n_learners]
        print 'run %s: %d learners' % (r, len(learners))
        x = range(len(learners))
        y = []
        for l in learners:
            best_so_far = max(y + [l.cv_judgment_metric])
            y.append(best_so_far)

        line, = plt.plot(x, y, '-', label=str(r.id))
        lines.append(line)

    plt.xlabel('learners')
    plt.ylabel(r.metric)
    plt.legend(handles=lines)
    plt.show()

def print_summary(db, rid):
    run = db.get_datarun(rid)
    ds = db.get_dataset(run.dataset_id)
    print
    print 'Dataset %s' % ds
    print 'Datarun %s' % run

    learners = db.get_learners(datarun_id=rid)
    print 'Learners: %d total' % len(learners)

    best = db.get_best_learner(datarun_id=run.id)
    if best is not None:
        score = best.cv_judgment_metric
        err = 2 * best.cv_judgment_metric_stdev
        print 'Best result overall: learner %d, %s = %.3f +- %.3f' % (best.id,
                                                                      run.metric,
                                                                      score, err)

    # maps algorithms to sets of frozen sets, and frozen sets to lists of
    # learners
    alg_map = {a: defaultdict(list) for a in db.get_algorithms(datarun_id=rid)}

    for l in learners:
        fs = db.get_frozen_set(l.frozen_set_id)
        alg_map[fs.algorithm][fs.id].append(l)

    for alg, fs_map in alg_map.items():
        print
        print 'algorithm %s:' % alg

        learners = sum(fs_map.values(), [])
        errored = len([l for l in learners if l.status ==
                       LearnerStatus.ERRORED])
        complete = len([l for l in learners if l.status ==
                        LearnerStatus.COMPLETE])
        print '\t%d errored, %d complete' % (errored, complete)

        best = db.get_best_learner(datarun_id=run.id, algorithm=alg)
        if best is not None:
            score = best.cv_judgment_metric
            err = 2 * best.cv_judgment_metric_stdev
            print '\tBest: learner %s, %s = %.3f +- %.3f' % (best, run.metric,
                                                           score, err)