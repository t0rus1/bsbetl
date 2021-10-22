//alert('If you see this alert, then the custom JavaScript script has run!')

// Temporarily disabled
// When the user scrolls down 100px from the top of the document, show the button
// window.onscroll = function() 
// { 
//     //alert('oy');
//     scrollFunction();
// };

function scrollFunction() 
{
    // the button 'scrollBtn' is assumed to present in the DOM
    // see index.py for its declaration
    var scrollbutton = document.getElementById("scrollBtn");
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) 
    {
        scrollbutton.style.display = "block";
    } 
    else 
    {
        scrollbutton.style.display = "none";
    }
}

/* This plain js function is encapsulated below in order to use it with DASH:
function topFunction() {
  // When the user clicks on the button, scroll to the top of the document
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}
*/

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        top_function: function() {
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
            return '';
        }
    }
});