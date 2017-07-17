from elasticsearch import Elasticsearch
from collections import defaultdict, OrderedDict
import operator


QUERIES = {"152501": "recent immigration order obama",
           "152502": "immigration 20th century",
           "152503": "illegal immigration"}

es = Elasticsearch()


def getResult(query, topicID, indexName, type):
    try:
        res = None
        try:
            res = es.search(index=indexName, doc_type=type, _source_include=['docno', 'url'], body={
                "query": {
                    "match": {
                        "text": query
                    }
                },
                'size': 200
            })
        except Exception, e:
            print e.message

        resultDict = defaultdict(lambda: 0.0)
        for hit in res['hits']['hits']:
            resultDict[hit['_source']['docno']] = float(hit['_score'])

        return resultDict


    except Exception, e:
        print e.message


def write(resultDict,topicID):
    with open('result.txt', 'a+') as f:
        for docId,score in resultDict.iteritems():
            f.write(str(topicID)+ ' Q0 ' + str(docId.encode('utf-8','ignore')) + ' ' + str(score)+ ' Exp\n')


if __name__ == '__main__':
    for topicID in QUERIES:
        result = getResult(str(QUERIES[topicID]), topicID, 'mi', 'document')
        write(OrderedDict(sorted(result.iteritems(), key=operator.itemgetter(1), reverse=True)),topicID)
