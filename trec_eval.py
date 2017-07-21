import sys
from collections import defaultdict, OrderedDict
import operator
import math
import matplotlib.pyplot as plt

# Initialize some arrays.

recalls = (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
cutoffs = (5, 10, 15, 20, 30, 100, 200, 500, 1000)


# Now take the values from the data array (four at a time) and
# put them in a data structure.  Here's how it will work.
#
# %qrel is a hash whose keys are topic IDs and whose values are
# references to hashes.  Each referenced hash has keys which are
# doc IDs and values which are relevance values.  In other words...
#
# %qrel				The qrel hash.
# $qrel{$topic}			Reference to a hash for $topic.
# $qrel{$topic}->{$doc_id}	The relevance of $doc_id in $topic.
#
# %num_rel			Hash whose values are (expected) number
#				of docs relevant for each topic.

def read_qrel(file_qrel):
    temp_qrel = defaultdict(lambda: defaultdict(lambda: 0))
    temp_num_rel = defaultdict(lambda: 0)

    f = open(file_qrel, 'r')
    l = f.readlines()
    for line in l:
        try:
            topic, dummy, doc_id, rel = line.split('<:>')
            rel = int(rel)
            temp_qrel[int(topic)][doc_id] = rel
            if rel > 0:
                temp_num_rel[int(topic)] += 1
            else:
                temp_num_rel[int(topic)] += 0
        except Exception, e:
            print e
    f.close()
    return temp_qrel, temp_num_rel


# Process the trec_file data in much the same manner as above.

def read_trec(file_result):
    temp_trec = defaultdict(lambda: {})

    f = open(file_result, 'r')
    l = f.readlines()
    for line in l:
        try:
            topic, dummy, doc_id, dummy, score, dummy = line.split('<:>')
            temp_trec[int(topic)][doc_id] = float(score)
        except Exception, e:
            print e
    f.close()
    temp_trec = OrderedDict(sorted(temp_trec.items()))
    return temp_trec


def computeDCG(rel_list, num_ret):
    dc_value = float(rel_list[0])
    for i in range(1, num_ret):
        dc_value += float(rel_list[i]) / math.log(1.0 + i)
    return dc_value
    # dc_value = 0.0
    # for i in range(0, num_ret):
    #     dc_value += float(2**rel_list[i] - 1.0) / math.log(2.0 + i)
    # return dc_value


def eval_print(topic, num_ret, total_no_relavant_docs, num_rel_ret, prec_at_recalls, avg_prec, prec_at_cutoffs, r_prec,
               F1_at_cutoffs, nDCG):
    print "\nQueryid (Num):    %5d\n" % topic
    print "Total number of documents over all queries\n"
    print "    Retrieved:    %5d\n" % num_ret
    print "    Relevant:     %5d\n" % total_no_relavant_docs
    print "    Rel_ret:      %5d\n" % num_rel_ret
    print "Interpolated Recall - Precision Averages:\n"
    print "    at 0.00       %.4f\n" % prec_at_recalls[0]
    print "    at 0.10       %.4f\n" % prec_at_recalls[1]
    print "    at 0.20       %.4f\n" % prec_at_recalls[2]
    print "    at 0.30       %.4f\n" % prec_at_recalls[3]
    print "    at 0.40       %.4f\n" % prec_at_recalls[4]
    print "    at 0.50       %.4f\n" % prec_at_recalls[5]
    print "    at 0.60       %.4f\n" % prec_at_recalls[6]
    print "    at 0.70       %.4f\n" % prec_at_recalls[7]
    print "    at 0.80       %.4f\n" % prec_at_recalls[8]
    print "    at 0.90       %.4f\n" % prec_at_recalls[9]
    print "    at 1.00       %.4f\n" % prec_at_recalls[10]
    print "Average precision (non-interpolated) for all rel docs(averaged over queries)\n"
    print "                  %.4f\n" % avg_prec
    print "Precision:\n"
    print "  At    5 docs:   %.4f\n" % prec_at_cutoffs[0]
    print "  At   10 docs:   %.4f\n" % prec_at_cutoffs[1]
    print "  At   15 docs:   %.4f\n" % prec_at_cutoffs[2]
    print "  At   20 docs:   %.4f\n" % prec_at_cutoffs[3]
    print "  At   30 docs:   %.4f\n" % prec_at_cutoffs[4]
    print "  At  100 docs:   %.4f\n" % prec_at_cutoffs[5]
    print "  At  200 docs:   %.4f\n" % prec_at_cutoffs[6]
    print "  At  500 docs:   %.4f\n" % prec_at_cutoffs[7]
    print "  At 1000 docs:   %.4f\n" % prec_at_cutoffs[8]
    print "R-Precision (precision after R (= num_rel for a query) docs retrieved):\n"
    print "    Exact:        %.4f\n" % r_prec
    print "***********************************************************"
    print "F1-Measure:\n"
    print "  At    5 docs:   %.4f\n" % F1_at_cutoffs[0]
    print "  At   10 docs:   %.4f\n" % F1_at_cutoffs[1]
    print "  At   15 docs:   %.4f\n" % F1_at_cutoffs[2]
    print "  At   20 docs:   %.4f\n" % F1_at_cutoffs[3]
    print "  At   30 docs:   %.4f\n" % F1_at_cutoffs[4]
    print "  At  100 docs:   %.4f\n" % F1_at_cutoffs[5]
    print "  At  200 docs:   %.4f\n" % F1_at_cutoffs[6]
    print "  At  500 docs:   %.4f\n" % F1_at_cutoffs[7]
    print "  At 1000 docs:   %.4f\n" % F1_at_cutoffs[8]
    print "nDCG for docs retrieved :\n"
    print "    Exact:        %.4f\n" % nDCG


def plotGraph(prec_at_recalls, topic):
    plt.plot(recalls, prec_at_recalls)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curves")
    plt.savefig("./graphs/%s.png" % topic)
    plt.close()


def computePrecision(trec, qrel, num_rel, all_query):
    num_of_topics = len(trec)
    tot_num_ret = 0
    tot_num_rel = 0
    tot_num_rel_ret = 0
    sum_avg_prec = 0.0
    sum_r_prec = 0.0
    sum_nDCG = 0.0
    sum_prec_at_cutoffs = [0.0] * len(cutoffs)
    sum_f1_at_cutoffs = [0.0] * len(cutoffs)
    sum_prec_at_recalls = [0.0] * len(recalls)

    for topic, docMap in trec.iteritems():

        if (num_rel[topic] == 0):
            continue

        len_list = len(docMap) + 1
        num_ret = 0  # Initialize number retrieved.
        num_rel_ret = 0  # Initialize number relevant retrieved.
        sum_prec = 0  # Initialize sum precision.
        prec_list = [None] * 1001
        rec_list = [None] * 1001
        rel_list = [None] * 1000
        total_no_relavant_docs = float(num_rel[topic])

        # Now sort doc IDs based on scores and calculate stats.
        # Note:  Break score ties lexicographically based on doc IDs.
        # Note2: Explicitly quit after 1000 docs to conform to TREC while still
        #        handling trec_files with possibly more docs.

        sortedMap = sorted(docMap.iteritems(), key=operator.itemgetter(1), reverse=True)

        for doc_id, score in sortedMap:
            temp_rel = float(qrel[topic][doc_id])
            rel_list[num_ret] = temp_rel
            num_ret += 1

            if temp_rel > 0.0:
                sum_prec += float((1.0 + num_rel_ret)) / num_ret
                num_rel_ret += 1

            prec_list[num_ret] = float(num_rel_ret) / num_ret
            rec_list[num_ret] = float(num_rel_ret) / total_no_relavant_docs

            if num_ret >= 1000:
                break

        avg_prec = sum_prec / total_no_relavant_docs

        # Fill out the remainder of the precision/recall lists, if necessary.

        final_recall = float(num_rel_ret) / total_no_relavant_docs

        # change 1001 to len list

        for i in range(num_ret + 1, 1001):
            prec_list[i] = num_rel_ret / i
            rec_list[i] = final_recall

        # Now calculate precision at document cutoff levels and R-precision.
        # Note that arrays are indexed starting at 0...

        prec_at_cutoffs = []
        F1_at_cutoffs = []

        for k in cutoffs:
            prec = prec_list[k]
            recall = rec_list[k]
            f1 = 0.0
            prec_at_cutoffs.append(prec)
            if prec > 0.0 and recall > 0.0:
                f1 = (2.0 * prec * recall) / (prec + recall)

            F1_at_cutoffs.append(f1)

        # Now calculate R-precision.

        r_prec = None
        if total_no_relavant_docs > num_ret:
            r_prec = float(num_rel_ret) / total_no_relavant_docs
        else:
            r_prec = prec_list[int(total_no_relavant_docs)]

        # Now calculate interpolated precisions...

        max_prec = 0.0;
        for i in range(1000, 0, -1):
            if (prec_list[i] > max_prec):
                max_prec = prec_list[i]
            else:
                prec_list[i] = max_prec

        # Finally, calculate precision at recall levels.
        prec_at_recalls = []
        i = 1
        for r in recalls:
            while (i <= 1000 and rec_list[i] < r):
                i += 1
            if i <= 1000:
                prec_at_recalls.append(prec_list[i])
            else:
                prec_at_recalls.append(0.0)

        plotGraph(prec_at_recalls, topic)
        # Now update running sums for overall stats.

        tot_num_ret += num_ret
        tot_num_rel += total_no_relavant_docs
        tot_num_rel_ret += num_rel_ret

        for i in range(0, len(cutoffs)):
            sum_prec_at_cutoffs[i] += prec_at_cutoffs[i]
            sum_f1_at_cutoffs[i] += F1_at_cutoffs[i]

        for i in range(0, len(recalls)):
            sum_prec_at_recalls[i] += prec_at_recalls[i]

        sum_avg_prec += avg_prec
        sum_r_prec += r_prec

        # Compute DCG
        calNDCG = computeDCG(rel_list, num_ret)
        idealNDCG =computeDCG(sorted(rel_list, reverse=True), num_ret)
        if not all(v == 0.0 for v in rel_list) and idealNDCG != 0.0:
            nDCG =  float(calNDCG)/idealNDCG
        else:
            nDCG = 0.0
        sum_nDCG += nDCG

        # Print stats on a per query basis if requested.

        if all_query:
            eval_print(int(topic), num_ret, total_no_relavant_docs, num_rel_ret, prec_at_recalls, avg_prec,
                       prec_at_cutoffs, r_prec, F1_at_cutoffs, nDCG)

    # Now calculate summary stats.

    avg_prec_at_cutoffs = []
    avg_f1_at_cutoffs = []
    for i in range(0, len(cutoffs)):
        avg_prec_at_cutoffs.append(sum_prec_at_cutoffs[i] / num_of_topics)
        avg_f1_at_cutoffs.append(sum_f1_at_cutoffs[i] / num_of_topics)

    avg_prec_at_recalls = []
    for i in range(0, len(recalls)):
        avg_prec_at_recalls.append(sum_prec_at_recalls[i] / num_of_topics)

    mean_avg_prec = float(sum_avg_prec) / num_of_topics
    avg_r_prec = float(sum_r_prec) / num_of_topics
    avg_nDCG = float(sum_nDCG) / num_of_topics
    plotGraph(avg_prec_at_recalls, "All_Combinedcls")
    eval_print(num_of_topics, tot_num_ret, tot_num_rel, tot_num_rel_ret, avg_prec_at_recalls, mean_avg_prec,
               avg_prec_at_cutoffs, avg_r_prec, avg_f1_at_cutoffs, avg_nDCG)


if __name__ == '__main__':
    if (len(sys.argv)) == 4:
        if sys.argv[1] == '-q':
            file_qrel = sys.argv[2]
            file_result = sys.argv[3]
            qrel, num_rel = read_qrel(file_qrel)
            trec = read_trec(file_result)
            computePrecision(trec, qrel, num_rel, True)
        else:
            print "Usage:  trec_eval [-q] <qrel_file> <trec_file>\n\n"
    elif (len(sys.argv)) == 3:
        file_qrel = sys.argv[1]
        file_result = sys.argv[2]
        qrel, num_rel = read_qrel(file_qrel)
        trec = read_trec(file_result)
        computePrecision(trec, qrel, num_rel, False)
    else:
        print "Usage:  trec_eval [-q] <qrel_file> <trec_file>\n\n"
