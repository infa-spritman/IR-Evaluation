from elasticsearch import Elasticsearch
from collections import defaultdict, OrderedDict, Set
import operator

QUERIES = {"152501": "recent immigration order obama",
           "152502": "immigration 20th century",
           "152503": "illegal immigration"}

es = Elasticsearch()


def getResult(query, indexName, type):
    documentSet = set()

    try:
        res = None
        try:
            res = es.search(index=indexName, doc_type=type, _source_include=['docno', 'url', 'grade'], body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "evaluate": True
                                }
                            },
                            {
                                "match": {
                                    "text": query
                                }
                            }
                        ]
                    }
                },
                "sort": [
                    "_score"
                ],
                'size': 500
            })
        except Exception, e:
            print e

        resultRankedListDict = defaultdict(lambda: 0.0)
        qrelDict = OrderedDict()
        for hit in res['hits']['hits']:
            docno = str(hit['_source']['docno'].encode('utf-8', 'ignore'))
            normaldocNo = docno.lower()
            if normaldocNo not in documentSet:
                # if len(documentSet) == 200:
                #     break
                resultRankedListDict[docno] = float(hit['_score'])
                qrelDict[docno] = int(hit['_source']['grade'])
                documentSet.add(normaldocNo)

        return resultRankedListDict, qrelDict


    except Exception, e:
        print e


def writeRankedList(resultDict, topicID):
    rank = 1
    with open('result_1000.txt', 'a+') as f:
        for docId, score in resultDict.iteritems():
            f.write(str(topicID) + '<:>Q0<:>' + docId + '<:>' + str(rank) + '<:>' + str(score) + '<:>Exp\n')
            rank += 1


def writeQrel(qrel, topicID):
    with open('qrel_crawled.txt', 'a+') as f:
        for docId, grade in qrel.iteritems():
            f.write(str(topicID) + '<:>0<:>' + docId + '<:>' + str(grade) + '\n')


if __name__ == '__main__':
    for topicID in OrderedDict(sorted(QUERIES.items())):
        print topicID
        result, qrel = getResult(str(QUERIES[topicID]), 'mi', 'document')
        #writeRankedList(OrderedDict(sorted(result.iteritems(), key=operator.itemgetter(1), reverse=True)), topicID)
        writeQrel(qrel, topicID)
