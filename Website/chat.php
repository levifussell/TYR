<!DOCTYPE html>
<html>
	<head>
		<?php
		$servername = "tyr.czavorwfa0ij.eu-west-2.rds.amazonaws.com";
		$username = "admin";
		$password = "Edin40214986";
		$dbname = "messages";

		// Create connection
		$conn = new mysqli($servername, $username, $password, $dbname);
		// Check connection
		if ($conn->connect_error) {
		   die("Connection failed: " . $conn->connect_error);
		}


		//$conn->close();
		?>
		<link rel="stylesheet" type="text/css" href="styles.css">
		<script type="text/javascript" src="http://code.jquery.com/jquery-latest.js"></script>
        <script src="js/processing.min.js"></script>
        <!--<script type="text/javascript" src="js/mainJS.js"></script>-->
	</head>
	<body>
        <!--<canvas id="myCanvas" resize="true"></canvas>-->

		<div class="header">
			TIME2TALK
			<a class='number'>+44087668865</a>
		</div>

        <!--<div class="leaderboardTitle">-->
            <!--Top Queries:-->
        <!--</div>-->
        <div class="big">
            <div class="pagewrap" id="hello">
                <div class="container" id="cont1">
                </div>
            </div>

            <div class="leaderboard">
                <canvas data-processing-sources="mainPDE.pde"></canvas>
                <div id="overlay">
									<?php
									$sql = "SELECT unikey, text_message, date_time FROM texts";
									$result = $conn->query($sql);

									if ($result->num_rows > 0) {
									   // output data of each row
									   while($row = $result->fetch_assoc()) {
									       echo $row["text_message"]. "<br>";
									   }
									} else {
									   echo "0 results";
									}
									?>
                </div>
            </div>
        </div>

		<script type="text/javascript">
		$(document).ready(function(){
					var count = 0;
							var html1 = '';
			$.getJSON( "texts.json", function( data ) {
					$.each(data, function(key, value){
						html1 += '<div class="bubble">';
					html1 += '<a for="'+value+'">'+value+': </a>';
						html1 += '<a for="'+key+'">'+key+'</a>';
						html1 += '</div>';
					});
				$('#cont1').html(html1);
				});

		 $("#form1").click(function(){

		   var form_data = {
				'me': $('#yepyep').val()
			};

			var json_text = JSON.stringify(form_data, null, 1);
		   				var html2 = '';
		   $.getJSON( "submit.json", function( data ) {
				$.each(data, function(key, value){
					html2 += '<div class="bubble bubble--alt" id="bub' + count + '">';
					html2 += '<a for="'+key+'">'+key+': </a>';
					html2 += '<a for="'+$('#yepyep').val()+'">'+$('#yepyep').val()+'</a>';
					html2 += '</div>';
					$('#yepyep').val("");
				});
				var obj = document.getElementById("hello");
				obj.scrollTop = obj.scrollHeight * 2;
			var htmlOld = $('#cont1').html();
			$('#cont1').html(htmlOld + html2);
			//$('#bub' + count).slideToggle(10);
			//$('#bub' + count).slideToggle();
			count++;
			});
			});

		 });
		</script>

		<div id ="form">
			<textarea class='textbox1' name="myTextBox" id="yepyep" >
			</textarea>
			<form id="form1">
				<input class="button" type="button" id="button1" value='Send'/>
			</form>
		</div>
	</body>
</html>
