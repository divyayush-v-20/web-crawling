(function() {
    function getXPathNodes(xpathExpression, contextNode = document) {
        const iterator = document.evaluate(
            xpathExpression,
            contextNode,
            null,
            XPathResult.ORDERED_NODE_ITERATOR_TYPE,
            null
        );
        const nodes = [];
        let node;
        while ((node = iterator.iterateNext())) {
            nodes.push(node);
        }
        return nodes;
    }

    let episodeNameNodes = getXPathNodes("/html/body/section/div/div/div/section/div/div/div/div/h3/text()");
    let seasonInfoNodes = getXPathNodes("/html/body/section/div/div/div/section/div/div/div/div/strong/span[1]/text()");
    let episodeInfoNodes = getXPathNodes("/html/body/section/div/div/div/section/div/div/div/div/strong/span[2]/text()");
    let airDateNodes = getXPathNodes("/html/body/section/div/div/div/section/div/div/div/div/strong[2]/text()");

    let length = seasonInfoNodes.length;

    class ShowMetaData {
        constructor(episodeName, seasonNumber, episodeNumber, airDate) {
            this.episodeName = episodeName;
            this.seasonNumber = seasonNumber;
            this.episodeNumber = episodeNumber;
            this.airDate = airDate;
        }
    }

    const getMetaData = (episodeNameNodes, seasonInfoNodes, episodeInfoNodes, airDateNodes) => {
        let resultObjects = [];
        for (let i = 0; i < length; i++) {
            const epName = episodeNameNodes[i] ? (episodeNameNodes[i].textContent || episodeNameNodes[i].data) : null;
            const sNum = seasonInfoNodes[i] ? (seasonInfoNodes[i].textContent || seasonInfoNodes[i].data) : null;
            const epNum = episodeInfoNodes[i] ? (episodeInfoNodes[i].textContent || episodeInfoNodes[i].data) : null;

            const aDate = airDateNodes[i] ? (airDateNodes[i].textContent || airDateNodes[i].data)?.trim() : null;

            resultObjects.push(
                new ShowMetaData(epName, sNum, epNum, aDate)
            );
        }
        return resultObjects;
    };

    return JSON.stringify(getMetaData(episodeNameNodes, seasonInfoNodes, episodeInfoNodes, airDateNodes));
})();

