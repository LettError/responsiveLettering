


// edits 20150529

// mathImage object
// takes 4 names of svg files
// loads them with snap
// then makes 2 axis interpolation
// that fill the parent box.
// factor 1: width
// factor 2: play

// With thanks to Jérémie Hornus, Nina Stössinger, Nick Sherman, Andrew Johnson, Petr van Blokland and Gerrit Noordzij.

		// tools
		function roundToTwo(num) {    
			return +(Math.round(num + "e+2")  + "e-2");
		}
		function randomIntFromInterval(min,max)
		{
		    return Math.floor(Math.random()*(max-min+1)+min);
		}

		function value(v){
			return "<span class='value'>"+v+"</span>"
		}

// mathshape class
function MathShape(elementId, miURL){
	this.shapeVersion = "0.3";
	this.elementId = elementId;
	this.reporterElementId = "#mathShapeReporter";
	this.masterPaths = [];
	this.root = miURL;
	this.mastersLoaded = [];	// the order in which the masters have actually loaded
	this.masterBounds = [];		// min max bounds of the masters (we get wrong results from snap)
	this.sizeFactor = 0.5;			// factor1 width/height ratio
	this.playFactor = 1.0;			// factor2
	this.currentLoadIndex = 0;	// keep track of the number of files we loaded
	this.svgLoaded = false;		// are we done?
	this.masterData = [];		// all the loaded svg data
	this.extrapolateMin = 0;	// extrapolate minimum
	this.extrapolateMax = 1.25;		// extrapolate maximum
	this.boundsRatio = 0			// ratio of the current bounds
	this.parentRatio = 0			// ratio of the parent bounds
	this.shapeFill = "white";			// default fill color
	this.shapeStroke = "#000";		// default stroke color
	this.shapeFillOpacity = 1;		// default fill opacity
	this.fitHeight = true;			// fit the height of the parent vertically
	this.alignment = 'right';
	this.strokeWidth = 2		// default stroke width
	this.parentWidth = 0;		// whatever the latest width we know of the parent
	this.parentHeight = 0;		// whatever the latest height we know of the parent
}
MathShape.prototype.loadLocal = function(){
	// load the data for this mathShape from the stuff available in this page. 
	this.snap = Snap(this.elementId);
	this.masterPaths = data['files'];
	this.masterBounds = data['sizebounds'];
	this.extrapolateMin = data['extrapolatemin'];
	this.extrapolateMax = data['extrapolatemax'];
	this.designspace = "twobyone";	//data['designspace'];
	this.onLoadedLocal(Snap('#narrow-thin'));
	this.onLoadedLocal(Snap('#wide-thin'));
	this.onLoadedLocal(Snap('#narrow-bold'));
	this.onLoadedLocal(Snap('#wide-bold'));
	this.svgLoaded = true;
	this.calculateFactors();
}
MathShape.prototype.loadFromWeb = function(){
	// load the data for this mathshape from the url
	this.snap = Snap(this.elementId);
	var self = this;	// http://stackoverflow.com/questions/2325866/assigning-scope-amongst-jquery-getjson-and-a-js-class
	var miPath = this.root+"/files.json";
	// console.log("miPath", miPath);

	jQuery.getJSON(miPath, {}, function(data){
		// console.log(typeof data['sizebounds'][0][0]);		//[[247, 751], [3000,750]]);
		self.masterPaths = data['files'];
		self.masterBounds = data['sizebounds'];
		self.extrapolateMin = data['extrapolatemin'];
		self.extrapolateMax = data['extrapolatemax'];
		self.designspace = "twobyone";	//data['designspace'];
		if(self.designspace == undefined){
			// if we have no designspace values, then assume it is two by two
			self.designspace = "twobyone";	//"twobytwo";
		}
		self.loadNextMaster();
	});

	$(this.elementId).click(function callbackClick(data){
		console.log("click!", self);
		self.breathe(0);
	});
	// console.log(this+" init masterData", this.masterData);
	// console.log("parent size", this.getParentSize());
	// this.makeReporter();
}
MathShape.prototype.updateReporter = function(){
	// if we happen to have an element named mathShapeReporter
	// add some telemetry to this element so we can see how we are doing. 
	// This needs to be cleaned up:
	// - can not rely on the elements present in the target page.
	// - make our own elements should be better
	// - also: some reporting takes longer.
	if(this.masterData!=undefined){
		$('#mathShapeMasterBounds').html("bounds "+value(this.masterBounds));
		$('#mathShapeName').html(value(this.root) + " pts "+value(this.masterData[0].length));
	}
	$('#mathShapeExtrapolate').html("min "+value(this.extrapolateMin)+", max "+value(this.extrapolateMax));
	$('#mathShapeRatio').html("ratio "+value(roundToTwo(this.boundsRatio))+"<br>parent "+value(roundToTwo(this.parentRatio)));
	

	
	// $('#mathShapeSizeFactor').text("size factor "+this.sizeFactor);
	// $('#mathShapePlayFactor').text("play factor "+this.playFactor);
}
MathShape.prototype.breathe = function(factor){
	//  redraw with the current size
	// animate the other factor
	this.playFactor = factor;
	if(this.svgLoaded==true){
		this.calculateFactors();
	}
	// else {
	// 	console.log("breathe, but not fully loaded yet");
	// }
}
MathShape.prototype.setFill = function(color, opacity){
	// set the preferred color and opacity
	this.shapeFill = color;
	if(opacity!=undefined){
		self.shapeFillOpacity = opacity;
	}
}
MathShape.prototype.setAlignment = function(alignment){
	// set the preferred alignment in the parent.
	this.alignment = alignment;
}
MathShape.prototype.ip = function(a, b, f){
	// interpolate function
	return a + f * (b-a);
};
MathShape.prototype.fc = function(a, b, c){
	// get factor from min / max and value.
	return (c-a)/(b-a);
};
MathShape.prototype.getParentSize = function(){
	// obtain the height and width of the parent
	return [$(this.elementId).parent().width(), $(this.elementId).parent().height()];
}
MathShape.prototype.loadNextMaster = function(){
	// load the svg masters, in sequence.
	// console.log(this+"loadNextMaster", this);
	if(this.currentLoadIndex<this.masterPaths.length){
		// console.log("\tnow loading "+this.masterPaths[this.currentLoadIndex]+" from "+this.root);
		Snap.load(this.masterPaths[this.currentLoadIndex], this.onLoaded, this);	// add the !@#$ scope!
	} else {
		this.calculateFactors();
	}
}
MathShape.prototype.calculateSize = function(){
	// calculate the size according to the current factors.
	// we want to calculate the size based on the masterBounds
	// because those might be different from the actual bounds
	// of the shape. (So that the shape can have some margin to
	// to the edge of the;box.)
	var currentWidth = 0;
	var currentHeight = 0;
	// interpolate the horizontal component fo the masterbounds
	// the vertical is the same, right?
	currentWidth = this.ip(this.masterBounds[0][0], this.masterBounds[1][0], this.sizeFactor);
	currentHeight = this.masterBounds[0][1]
	return [currentWidth, currentHeight];
}
MathShape.prototype.calculateShapeTwoByTwo = function(){
	var resultPath = [];
	// $( "#outline" ).text('');
	// when all masters are loaded
	if(this.masterData[0]==null){
		// still loading it seems
		return;
	}
	var ptLength = this.masterData[0].length;
	for (var i = 0; i < ptLength; i++) {
		var newCommand = [this.masterData[0][i][0]]; // add the command
		// iterate through the command args
		switch(this.masterData[0][i][0]){
			case 'H':
				// console.log("calculateShape H");
				// handle horizontal segment
				var x1 = this.ip(this.masterData[0][i][1], this.masterData[1][i][1], this.sizeFactor);
				var x2 = this.ip(this.masterData[2][i][1], this.masterData[3][i][1], this.sizeFactor);
				var x = this.ip(x1, x2, this.playFactor);
				newCommand.push(x);
				break;
			case 'V':
				// console.log("calculateShape V");
				// handle vertical segment
				var y1 = this.ip(this.masterData[0][i][1], this.masterData[1][i][1], this.sizeFactor);
				var y2 = this.ip(this.masterData[2][i][1], this.masterData[3][i][1], this.sizeFactor);
				var y = this.ip(y1, y2, this.playFactor);
				newCommand.push(y);
				break;
			case 'L':
			default:
				// console.log("calculateShape default");
				// handle all the other segments
				for (var args=1; args<this.masterData[0][i].length-1; args+=2){
					var x1 = this.ip(this.masterData[0][i][args], this.masterData[1][i][args], this.sizeFactor);
					var y1 = this.ip(this.masterData[0][i][args+1], this.masterData[1][i][args+1], this.sizeFactor);
					var x2 = this.ip(this.masterData[2][i][args], this.masterData[3][i][args], this.sizeFactor);
					var y2 = this.ip(this.masterData[2][i][args+1], this.masterData[3][i][args+1], this.sizeFactor);
					// console.log(args, newCommand);
					var x = this.ip(x1, x2, this.playFactor);
					var y = this.ip(y1, y2, this.playFactor);
					// console.log(x, y);
					newCommand.push(x);
					newCommand.push(y);
				};
				break;
		};
		// // show the calculated instruction on the page
		// // show the contributing masters on the page
		// $( "#outline" ).append("<br>"+i+' '+this.masterData[0][i][0]+" "+this.masterData[1][i][0]+" "+this.masterData[2][i][0]+" "+this.masterData[3][i][0]+" <b>"+newCommand+"</b>");
		resultPath.push(newCommand);
	};
	// $( "#outline" ).append("</ul>");
	this.snap.clear()
	var newPath = this.snap.path(resultPath);
	var bounds = Snap.path.getBBox(newPath);
	// paint instructions
	newPath.attr({'fill': this.shapeFill, 'opacity': this.shapeFillOpacity});
	this.snap.append(newPath);
	var centeringOffset = 0;
	this.boundsRatio = bounds.width / bounds.height;
	//this.parentRatio = this.parentWidth / this.parentHeight;
	if(this.boundsRatio<0.99*this.parentRatio){
		switch(this.alignment){
			// don't bother calculating the offset, just let our parent know the alignment
			case 'center':
				$(this.elementId).parent().attr('align', 'center');
				break;
			case 'right':
				$(this.elementId).parent().attr('align', 'right');
				break;
		}
	}
	// if the bounds of the resulting shape are not enough to fit the box,
	// center the image in the box
	if(this.fitHeight){
		var currentSize = this.calculateSize();
		this.snap.attr({ viewBox: "0 0 "+currentSize[0]+" "+currentSize[1]+" " });
		// this.snap.attr({ viewBox: "0 0 "+bounds.width+" "+bounds.height+" " });
	}
	// console.log("calculateShape done");
}

MathShape.prototype.onLoadedLocal = function(data){
	// when an svg is loaded locally
	// console.log("onLoadedLocal", data)
	outline = data.select("path")
	outline = Snap.parsePathString(outline);
	Snap.path.toAbsolute(outline);
	// console.log(this+" onLoadedLocal outline", outline);
	if(this.masterData==null){
		this.masterData = [];
	}
	this.masterData.push(outline);
	// console.log(this+" onLoadedLocal masterData", this.masterData);
	this.currentLoadIndex++;
	// console.log("onLoadedLocal done");
	// console.log("onLoadedLocal masterBounds", this.masterBounds);
};
MathShape.prototype.onLoaded = function(data){
	// when a svg is loaded, interpret the data.
	// when everything is loaded, calculate the image.
	// loadScore += 1;
	// console.log("onLoaded", data)
	outline = data.select("path")
	outline = Snap.parsePathString(outline);
	Snap.path.toAbsolute(outline);
	// console.log(this+" onLoaded outline", outline);
	// var imgBounds = Snap.path.getBBox(outline);

	// masterBounds.push([bounds.width, bounds.height]);
	if(this.masterData==null){
		this.masterData = [];
	}
	this.masterData.push(outline);
	// console.log(this+" onLoaded masterData", this.masterData);
	this.currentLoadIndex++;
	if(this.currentLoadIndex<this.masterPaths.length){
		// console.log("onLoaded 1");
		this.loadNextMaster();
	} else {
		// console.log("onLoaded 2");
		this.svgLoaded = true;
	};
	if (this.svgLoaded){
		// console.log("onLoaded 3");
		this.calculateFactors();
	};
	// console.log("onLoaded done");
};
MathShape.prototype.calculateFactors = function(){
	//	The svg image height is set to 100%.
	//	Therefor yhe window will scale the image to the right height.
	//	That means that we only have to calculate the appropriate width to fill the box.
	//	Take the width / height ration from the parent, then calculate
	//	the factors needed for the image to get the same ratio. 
	var width = $( this.elementId ).parent().outerWidth();
	var height = $( this.elementId ).parent().outerHeight();
	this.parentWidth = width;
	this.parentHeight = height;
	this.parentRatio = width/height; // we need to match this
	// $( "#sources" ).text('sources '+this.masterPaths);
	// $( "#windowRatio" ).text('parentRatio '+parentRatio);
	// $( "#width" ).text('parent width '+width);
	// $( "#height" ).text('parent height '+height);
	// check if we can calculate the factors based on the bounds
	// assume bounds are the same
	var mWidths = 0;
	var mHeights = 0;
	var minWidth = this.masterBounds[0][0];
	var maxWidth = this.masterBounds[0][0];
	var minHeight = this.masterBounds[0][1];
	var maxHeight = this.masterBounds[0][1];
	// $( "#initialBounds" ).text('initialbounds minWidth:'+ minWidth +' maxWidth '+ maxWidth +' minHeight '+ minHeight +' maxHeight '+ maxHeight);
	for(var i=1; i<this.masterBounds.length; i+=2){
		minWidth = Math.min(minWidth, this.masterBounds[i][0]);
		maxWidth = Math.max(maxWidth, this.masterBounds[i][0]);
		minHeight = Math.min(minHeight, this.masterBounds[i][1]);
		maxHeight = Math.max(maxHeight, this.masterBounds[i][1]);
	};
	// $( "#shapeBounds" ).text('shapebounds '+this.masterBounds + '\nminWidth:'+ minWidth +'\nmaxWidth'+ maxWidth +'\nminHeight'+ minHeight +'\nmaxHeight'+ maxHeight);
	this.sizeFactor = this.fc(minWidth, maxWidth, this.parentRatio*minHeight);
	// keep the factors within 0 and 1
	// factor 2 is controlled by other events.
	this.sizeFactor = Math.min(this.extrapolateMax, Math.max(this.extrapolateMin, this.sizeFactor));
	this.calculateShapeTwoByTwo();
}

// done