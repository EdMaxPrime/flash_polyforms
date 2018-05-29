console.log("ok");
function makePieChart(){
	d3.select("#chartModalLabel").text(document.getElementById("pieColumn").value);
	console.log(document.getElementById("pieColumn").value);
	var chart = c3.generate({
    bindto: '#chart',
    data: {
      columns: [
        ['data1', 30, 200, 100, 400, 150, 250],
        ['data2', 50, 20, 10, 40, 15, 25]
      ]
    },
    size: {
    	width: 200,
    	height: 200
    }
});
};