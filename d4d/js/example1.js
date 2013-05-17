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

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
    this.elem.innerHTML = text;
    //this.elem.style.left = (300 - this.elem.offsetWidth / 2) + 'px';
  }
};

var base_url = "http://54.243.221.116:8000/";

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
          color: "#f00"
      },
      //transition: $jit.Trans.Back.easeOut,
      duration:1000,
      Edge: {
          overridable: true,
          lineWidth: 2,
          color: "#088"
      },
      onBeforeCompute: function(node){
          Log.write("centering");
      },
      onBeforePlotLine: function(adj) {
          //adj.data.$lineWidth = Math.random() * 17 + 1;
          //console.log(adj.data);
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
              style.fontSize = "0.8em";
              style.color = "#ddd";

          } else if(node._depth == 2){
              style.fontSize = "0.7em";
              style.color = "#555";

          } else {
              style.display = 'none';
          }

          var left = parseInt(style.left);
          var w = domElement.offsetWidth;
          style.left = (left - w / 2) + 'px';
      },
      
      onComplete: function(){
          Log.write("done");

          //Build the right column relations list.
          //This is done by collecting the information (stored in the data property) 
          //for all the nodes adjacent to the centered node.
          var node = ht.graph.getClosestNodeToOrigin("current");
          // Parse assertion simply, assume it is of the form "concept relation concept"
          var assertion = node.id
          var relation = $("#assertion").val();
          var relation_index = assertion.indexOf(relation);
          var left = assertion.substring(0, relation_index-1).replace(" ", "_");
          var right = assertion.substring(relation_index+relation.length+1).replace(" ", "_");
          var query = "similar/".concat(left).concat("/").concat(relation).concat("/").concat(right).concat("/").concat($("#numResults").val()).concat("/").concat($("#threshold").val()*100).concat("/");
          var new_name = JSON.parse(httpGet(base_url.concat(query)));
          ht.loadJSON(new_name);
          ht.refresh();
          var html = "<h4>" + node.name + "</h4><b>Connections:</b>";
          html += "<ul>";
          node.eachAdjacency(function(adj){
              var child = adj.nodeTo;
              if (child.data) {
                  var rel = (child.data.band == node.name) ? child.data.relation : node.data.relation;
                  html += "<li>" + child.name + " " + "<div class=\"relation\">(relation: " + rel + ")</div></li>";
              }
          });
          html += "</ul>";
          $jit.id('inner-details').innerHTML = html;
      }
    });
    $("#assertionSelect").submit(function() {
      var left = $("#leftValue").val().replace(" ", "_");
      var right = $("#rightValue").val().replace(" ", "_");
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
