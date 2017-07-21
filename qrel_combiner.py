from collections import defaultdict, OrderedDict
import operator

def read_qrel(file_qrel):
    temp_qrel = defaultdict(lambda: OrderedDict())

    f = open(file_qrel, 'r')
    l = f.readlines()
    for line in l:
        try:
            topic, dummy, doc_id, rel = line.split('<:>')
            rel = int(rel)
            temp_qrel[int(topic)][doc_id] = rel


        except Exception, e:
            print e

    f.close()
    return temp_qrel


def calculateFgrade(grade, grade2, grade3):
    temp_map = defaultdict(lambda :0)
    temp_map[grade] +=1
    temp_map[grade2] +=1
    temp_map[grade3] +=1

    if temp_map[0]==1 and temp_map[1]==1 and temp_map[2]==1:
        return 1
    else:
        #sortmap = sorted(temp_map.items(), key=operator.itemgetter(1), reverse=True)
        for key, value in sorted(temp_map.items(), key=operator.itemgetter(1), reverse=True):
            return key


def writeQrel(qrel, topicID):
    with open('qrel_crawled.txt', 'a+') as f:
        for docId, grade in qrel.iteritems():
            f.write(str(topicID) + '<:>0<:>' + docId + '<:>' + str(grade) + '\n')


if __name__ == '__main__':
    final_qrel = defaultdict(lambda: OrderedDict())
    qrel_sushant = read_qrel('./files/qrels/qrel_crawled_sushant_500.txt')
    qrel_kd = read_qrel('./files/qrels/qrel_crawled_kd_500.txt')
    qrel_saurin = read_qrel('./files/qrels/qrel_crawled_saurin_500.txt')
    for topic, docmap in qrel_sushant.iteritems():
        documentset = set()
        for docId, grade in docmap.iteritems():
            if len(documentset) == 200:
                break
            if docId in qrel_kd[topic] and docId in qrel_saurin[topic]:
                grade2 = qrel_kd[topic][docId]
                grade3 = qrel_saurin[topic][docId]
                finalGrade = calculateFgrade(grade, grade2, grade3)
                final_qrel[topic][docId] = finalGrade
                documentset.add(docId)

    for topicID in OrderedDict(sorted(final_qrel.items())):
        print topicID
        writeQrel(final_qrel[topicID], topicID)
