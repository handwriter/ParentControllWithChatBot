startX = 0;
startY = 0;
currX = 0;
currY = 0;

String.format = function() {
      var s = arguments[0];
      for (var i = 0; i < arguments.length - 1; i++) {
          var reg = new RegExp("\\{" + i + "\\}", "gm");
          s = s.replace(reg, arguments[i + 1]);
      }
      return s;
};

function OnTopBarClicked(e) {
    console.log('OnMouseDown');
    httpPost("/startmovewindow")
}

function OnTopBarUnclicked() {
    console.log('OnMOuseUp');
}

// window.onload = () => {
//     console.log('onloadend');
// };

function httpPost(theUrl)
{
    var xhr = new XMLHttpRequest();
    xhr.open('POST', theUrl, true);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr.send()
    // xhr.send('user=person&pwd=password&organization=place&requiredkey=key');
}