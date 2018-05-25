$(function(){
	 
	  var bannerLength = $('.showList li').length;
	  for(i=0; i<bannerLength; i++){
		 
		  $('.showList li').eq(i).text(i+1)
	  }
	   $('.showList li').click(function(){
			 window.clearTimeout(timer)
			 $('.showList li').removeClass('special')
			 $(this).toggleClass('special')
			 thisImg = $(this).attr('img')
			 $('.banner2').css('background','url("'+ thisImg +' ")  no-repeat center 0')
			 $('.banner').animate({opacity:0},1000,function(){   $('.banner').css('background-image','url("'+ thisImg +'")').fadeTo("slow", 1000)    })
			 thisIndex = $(this).index()+1>=bannerLength ? 0 :  $(this).index()+1
			 timer = window.setTimeout( "$('.showList li').eq(thisIndex).trigger('click') ", 3000  )
	})
	//�Զ�����banner��case����
	timer = window.setTimeout( "$('.showList li').eq(1).trigger('click')"  , 3000  )
	window.setInterval( "$('.case-left-arrow').trigger('click')"  , 2000  )

})