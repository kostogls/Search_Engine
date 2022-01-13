import Crawler
import Query
import time
import Indexer_2


if __name__ == '__main__':

    ask = ''
    top_k = 10
    crawl_input = str(input("Give your crawl search: ")).split()

    myCrawler = Crawler.Crawler(crawl_input[0], int(crawl_input[1]), int(crawl_input[2]), int(crawl_input[3]))

    # In the loop below we are executing the crawl, the indexer and the query
    while True:
        time.sleep(5)

        theIndexer = Indexer_2.Indexer_2(myCrawler.docs_urls)
        pros = theIndexer.run_multithread()
        end = time.time()
        idf = theIndexer.get_idf(pros)
        tf_idf_results = theIndexer.get_tfidf(pros, idf)
        final_dic = theIndexer.get_indexer(pros)
        end2 = time.time()

        # Take the query
        theQuery = Query.Query(final_dic, idf, tf_idf_results)

        # Top k results that the user wants
        top_k = int(input("How many results do you want? "))
        theQuery.top_k(myCrawler.docs_urls, top_k)

        # Asking if you want to continue crawling/indexing/query
        ask = str(input("You want to continue? Yes/No ")).lower()
        if ask == 'yes':
            crawl_input = str(input("Give your crawl search: ")).split()
            myCrawler.lets_continue_crawling(crawl_input[0], int(crawl_input[1]), int(crawl_input[2]), int(crawl_input[3]))
        else:
            break




