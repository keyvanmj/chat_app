let messages = document.getElementById('messages')
$(document).ready(function(){
	$(messages).scroll(function () {
			if ($(this).scrollTop() > 500) {
				$('#back-to-top').fadeIn();
			} else {
				$('#back-to-top').fadeOut();
			}
		});
		// scroll body to 0px on click
		$('#back-to-top').click(function () {
			$(messages).animate({
				scrollTop:0
			}, 400);
			return false;
		});
});

