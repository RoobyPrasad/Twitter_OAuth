var fs = fs || {};

function convertToLinks(text) {
    var replaceText, replacePattern1;

    //URLs starting with http://, https://
    replacePattern1 = /(\b(https?):\/\/[-A-Z0-9+&amp;@#\/%?=~_|!:,.;]*[-A-Z0-9+&amp;@#\/%=~_|])/ig;
    replacedText = text.replace(replacePattern1, '<a class="colored-link-1" title="$1" href="$1" target="_blank">$1</a>');

    //URLs starting with "www."
    replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    replacedText = replacedText.replace(replacePattern2, '$1<a class="colored-link-1" href="http://$2" target="_blank">$2</a>');

    //returns the text result

    return replacedText;
}

(function(fs) {
    fs.main = {
        init : function(){
            fs.main.loadTweets();
        },
        loadTweets: function(){
            var oThis = this;
                $.ajax({
                    url: '/twitterapp/recent-tweets/',
                    error: function(){
                        console.log('Something wrong');
                    },
                    success: function(tweets){
                         oThis.displayTweet(tweets);
                    }
                });
        },

        displayTweet: function(tweets){
            var htmlBody = "";
            console.log(tweets);
            for (tweet in tweets){
                console.log(tweets[tweet].text);
                htmlBody += [
                        '<div class="test">',
                            '<div class="fl" style="width:80px;">',
                                '<img src='+tweets[tweet].user.profile_image_url_https+'>',
                            '</div>',
                            '<div class="fl" style="width:400px;">',
                                '<p><i>',
                                    convertToLinks(tweets[tweet].text),
                                '</p></i><p><small>',tweets[tweet].created_at,'</small></p>',
                            '</div>',
                            '<div class="clear"></div>',
                        '</div>'
                ].join("")
            }
            $('#tweetList').html(htmlBody);
        }
    }

})(fs)