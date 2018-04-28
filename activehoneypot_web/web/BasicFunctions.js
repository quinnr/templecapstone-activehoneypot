var data_transformed = [];
//Organize the JSON into a 2D array for easier access
function transformData(list) {
    data_transformed = [];
    var i = 0;
    var j;
    for (j in list) {
        data_transformed[i] = new Array(14);
        data_transformed[i][0] = list[j].attackerID;
        data_transformed[i][1] = list[j].ip_address;
        data_transformed[i][2] = list[j].username;
        data_transformed[i][3] = list[j].passwords;
        data_transformed[i][4] = list[j].time_of_day_accessed;
        data_transformed[i][5] = list[j].logFile;
        data_transformed[i][6] = list[j].sessions;
        data_transformed[i][7] = list[j].country;
        data_transformed[i][8] = list[j].city;
        data_transformed[i][9] = list[j].state;
        data_transformed[i][10] = list[j].logged_in;
        data_transformed[i][11] = list[j].uploaded_files;
        data_transformed[i][12] = list[j].date_accessed;
        data_transformed[i][13] = list[j].errorMsg;
        i++;
        //console.log("Added entry " + i + " to data_transformed");
    }
    console.log("click to open up 'transform_data' item below.");
    console.log(data_transformed);

    return data_transformed;
}

var password_list = [];
var password_count = [];

//Count the password frequency
function find_password_frequency(list) {
    password_list = [];
    password_count = [];
    for (var i = 0; i < list.length; i++) {
        if (!(list[i][3] === "")) {
            var ps = list[i][3].split(" ");

            for (var j = 0; j < ps.length; j++) {
                var index = password_list.indexOf(ps[j]);
                if (index === -1) {
                    password_list.push(ps[j]);
                    password_count.push(1);
                    console.log("Added password: " + ps[j] + " to the password_list");
                } else {
                    password_count[index] += 1;
                    console.log("Increased password " + ps[j] + " to " + password_count[index] + " in password_count");
                }
            }
        }
    }
    console.log("click to see 'password_list' below.");
    console.log(password_list);
    console.log("click to see 'password_count' below.");
    console.log(password_count);

    return [password_list, password_count];
}

var variable_list = [];
var variable_count = [];
//Count the variable frequency

function find_variable_frequency(list, list_index) {
    variable_list = [];
    variable_count = [];
    for (var i = 0; i < list.length; i++) {
        if (!(list[i][list_index] === "")) {
            var name = list[i][list_index];
            var index = variable_list.indexOf(name);
            if (index === -1) {
                variable_list.push(name);
                variable_count.push(1);
            } else {
                variable_count[index] += 1;
            }
        }
    }
    console.log("click to see 'variable_list' below.");
    console.log(variable_list);
    console.log("click to see 'variable_count' below.");
    console.log(variable_count);

    return [variable_list, variable_count];
}

var hour = [];
var sessionCounter = [];
//Use this to get the data on hours
function organize_hour_data(list) {
    hour = Array.from({length: 24}, (x, i) => i);
    sessionCounter = new Array(24).fill(0);

    for (var i = 0; i < list.length; i++) {

        if (!(list[i][4] === "")) {
            var timeString = list[i][4].substr(0, 2);
            var timeInt = parseInt(timeString);
            sessionCounter[timeInt] += 1;
        }
    }

    console.log("click to see 'hour' below.");
    console.log(hour);
    console.log("click to see 'sessionCounter' below.");
    console.log(sessionCounter);

    return [hour, sessionCounter];
}

var day = [];
var day_counter = [];

//Use this function to get the counted days

function organize_day_data(list) {
    day = Array.from({length: 7}, (x, i) => i);
    day_counter = new Array(7).fill(0);

    for (var k = 0; k < list.length; k++) {
        if (!(list[k][12] === "")) {
            var dayString = new Date(list[k][12]).getDay();
            var index = day.indexOf(dayString);

            day_counter[index] += 1;
        }
    }

    console.log("click to see 'day' below.");
    console.log(day);
    console.log("click to see 'day_counter' below.");
    console.log(day_counter);

    return [day, day_counter];

}
var data_percentage;
function get_percentages(data_count){
    data_percentage = Array.from(data_count.length).fill(0);
    
    var sum = data_count.reduce(add, 0);
    
    for(var k = 0; k < data_count.length; k++){
        data_percentage[k] = 100 * (data_count[k] / sum) ;
    }
    
    console.log("click to see 'data_count below.");
    console.log(data_count);
    console.log("click to see 'data_percentage' below.");
    console.log(data_percentage);
    
    return data_percentage;
    
}

function add(a, b) {
    return a + b;
}




