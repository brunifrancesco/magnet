function requestForView(path) {
	$.ajax({
  url: path
}).done(function(data) {
 	fillWithInfo(data);
});
}

function fillWithInfo(data){
		$("#content").html(data);
}

function processData(data){
	var tweets = data.children[0].children[1].children;
	var result = "";
	for(var i = 0; i < tweets.length; i++){
		var tweet = tweets[i];
		var text = tweet.children[0].textContent;
		var label = tweet.children[1].textContent;
		result += '<div  class="std_margin box" id="response"><div class="result"><b>'+text +"</b><span class='tweet_label'> "+ label+' </span></div></div>';
	}
	return result;

}

$(document).ready(function(){
	
	$(".index").click(
		function(){
			requestForView("intro");
		}
		);
	$(".tweets").click(
		function(){
			requestForView("tweets");
		}
		);
	$(".search").click(
		function(){
			requestForView("search");
		}
		);
});