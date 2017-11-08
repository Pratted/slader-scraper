//Remove all non-sense, ads, irrelevant material from webpage.

function removeElementsByClass(className){
    var elements = document.getElementsByClassName(className);

    while(elements.length > 0){
        elements[0].parentNode.removeChild(elements[0]);
    }
}

removeElementsByClass("question-feed question-and-answers-container");
removeElementsByClass("ads");
removeElementsByClass("field-group");
removeElementsByClass("button small submit");
removeElementsByClass("slader-stickers");
removeElementsByClass("cheatsheet-widget");
removeElementsByClass("primary");
removeElementsByClass("search");
removeElementsByClass("textbook-section top");
removeElementsByClass("textbook-header");
removeElementsByClass("inner ad main-top-ac");
removeElementsByClass("right");


document.getElementsByTagName("footer")[document.getElementsByTagName("footer").length-1].remove();
document.getElementsByTagName("header")[0].remove();

