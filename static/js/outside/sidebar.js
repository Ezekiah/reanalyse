var oo = oo || {}; oo.vars.sidebar = oo.vars.sidebar || {};

oo.sidebar = {  is_hidden:false, element:[] };
oo.sidebar.init = function(){
	oo.sidebar.is_hidden = false;
	oo.sidebar.element = $("sidebar");
	$("#collapse-menu").click( oo.sidebar.collapse );
	$("#expand-menu").click( oo.sidebar.expand );

	//$("#right-sidebar").height($("#left-side").height());


	$("#navbar").on('click','li',function(){
		$("#navbar li").removeClass('active')
		$(this).addClass('active');
	});
	$("#navbar").scrollToFixed({ limit:
		$('footer').offset().top - $("#navbar").height()
	});

	// scrollspy
	oo.sidebar.scrollspy.init();
}

oo.sidebar.collapse = function(){
	oo.sidebar.element.addClass("collapsed");
	$("#collapse-menu").hide();
	$("#expand-menu").show();
}

oo.sidebar.expand = function(){
	oo.sidebar.element.removeClass("collapsed");
	$("#collapse-menu").show();
	$("#expand-menu").hide();
}



oo.sidebar.scrollspy = {
	target: $("#navbar li"),
	previous: {
		wh:0,
		ws:0
	},
	timer:0,
	measure_on_parent:true
};
oo.sidebar.scrollspy.init = function(){
	// test visibility of the first element
	oo.sidebar.scrollspy.target = $("#navbar li a")

	$(window).scroll( oo.sidebar.scrollspy.pull );
	$(window).resize( oo.sidebar.scrollspy.pull );
}
oo.sidebar.scrollspy.spy = function(){
	clearTimeout( oo.sidebar.scrollspy.timer );
	oo.sidebar.scrollspy.timer = setTimeout( oo.sidebar.scrollspy.pull, 50 );

}

oo.sidebar.scrollspy.pull = function(){//oo.log("[oo.sidebar.scrollspy.pull]");

	// calm down. not each scroll!
	var wh = $(window).height()
	var ws = $(window).scrollTop()
	oo.sidebar.scrollspy.target.parent().removeClass("active");
	oo.sidebar.scrollspy.target.each( function( i, e){
		
		var e = $(this);
		var h = e.attr("href")
		if( h.indexOf("#") != 0 ){
			return;
		}

		var ht = $( h ).offset().top -36;
		if( oo.sidebar.scrollspy.measure_on_parent ){
			var hh = $( h ).parent().height(); // target height. It is visible??


		} else {
			var hh = $( h ).height();
		}
		



		oo.log( wh, ws, i, h,  ht, ht < wh + ws, ht + hh > ws );
		// visibility
		if( ht < wh + ws && ht + hh > ws ){
			// first element visible in page
			e.parent().addClass("active");
			return false;
		}

		
	});
}