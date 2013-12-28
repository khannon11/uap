var labelType, useGradients, nativeTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

// TODO this has to be changed depending to match the host we're running on
// so it knows where to send async requests to update the graph.
var base_url = "http://54.243.221.116:8000/";

// Basic http get wrapper
function httpGet(theUrl) {
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open("GET", theUrl, false);
  xmlHttp.send();
  return xmlHttp.responseText;
}
      
function init(){
    var infovis = document.getElementById('infovis');
    var w = infovis.offsetWidth - 50, h = infovis.offsetHeight - 150;
    
    //init Hypertree
    var ht = new $jit.Hypertree({
      //id of the visualization container
      injectInto: 'infovis',
      //canvas width and height
      width: w,
      height: h,
      //Change node and edge styles such as
      //color, width and dimensions.
      Node: {
          overridable: true,
          dim: 9,
          color: "#bd2031"
      },
      duration:1000,
      Edge: {
          overridable: true,
          lineWidth: 2,
          color: "#0000ff"
      },
      //Attach event handlers and add text to the
      //labels. This method is only triggered on label
      //creation
      onCreateLabel: function(domElement, node){
        domElement.innerHTML = node.name;
        $jit.util.addEvent(domElement, 'click', function () {
          ht.onClick(node.id, {
            onComplete: function() {
                ht.controller.onComplete();
            }
          });
        });
      },
      //Change node styles when labels are placed
      //or moved.
      onPlaceLabel: function(domElement, node){
          var style = domElement.style;
          style.display = '';
          style.cursor = 'pointer';
          if (node._depth <= 1) {
              style.fontSize = "15px";
              style.color = "#ddd";

          } else if(node._depth == 2){
             style.fontSize = "12px";
              style.color = "#555";

          } else {
              style.display = 'none';
          }

          var left = parseInt(style.left);
          var w = domElement.offsetWidth;
          style.left = (left - w / 2) + 'px';
      },
      
      onComplete: function(){
          //Build the right column relations list.
          //This is done by collecting the information (stored in the data property) 
          //for all the nodes adjacent to the centered node.
          var node = ht.graph.getClosestNodeToOrigin("current");
          // Parse assertion simply, assume it is of the form "concept relation concept"
          var assertion = node.id
          var relation = $("#assertion").val();
          var relation_index = assertion.indexOf(relation);
          var left = assertion.substring(0, relation_index-1).replace(" ", "_").toLowerCase();
          var right = assertion.substring(relation_index+relation.length+1).replace(" ", "_").toLowerCase();
          var query = "similar/".concat(left).concat("/").concat(relation).concat("/").concat(right).concat("/").concat($("#numResults").val()).concat("/").concat($("#threshold").val()*100).concat("/");
          var new_name = JSON.parse(httpGet(base_url.concat(query)));
          ht.loadJSON(new_name);
          ht.refresh();
      }
    });
    $("#assertionSelect").submit(function() {
      var left = $("#leftValue").val().replace(" ", "_").toLowerCase();
      var right = $("#rightValue").val().replace(" ", "_").toLowerCase();
      var query = "similar/".concat(left).concat("/").concat($("#assertion").val()).concat("/").concat(right).concat("/").concat($("#numResults").val()).concat("/").concat($("#threshold").val()*100).concat("/");
      var new_name = JSON.parse(httpGet(base_url.concat(query)));
      if (typeof new_name == "string" && new_name.substring(0, 2) == '!!') {
        alert(new_name.substring(3).concat(" is not in the database :("));
      } else {
        ht.loadJSON(new_name);
        ht.refresh();
        ht.onClick(new_name.id, {
          onComplete: function() {
              ht.controller.onComplete();
          }
        });
      }
    });
}
