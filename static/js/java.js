// Prevent dropdown menu from closing when click inside the form
$(document).on("click", ".action-buttons .dropdown-menu", function(e){
	e.stopPropagation();
});
  function myFunction1() {

        document.getElementById("myDIV1").style.display = "block";

        document.getElementById("myDIV2").style.display = "none";

        document.getElementById("myDIV3").style.display = "none";

      

    }

    function myFunction2() {

      document.getElementById("myDIV1").style.display = "none";

      document.getElementById("myDIV2").style.display = "block";

      document.getElementById("myDIV3").style.display = "none";

  

    }

    function myFunction3() {

      document.getElementById("myDIV1").style.display = "none";

      document.getElementById("myDIV2").style.display = "none";

      document.getElementById("myDIV3").style.display = "block";

    

    }

