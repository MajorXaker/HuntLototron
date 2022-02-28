function getCoords(event) {
    var x = event.offsetX;
    var y = event.offsetY;
    return {'x': x ,'y': y};
};

function getSize(element) {

    
    var element = document.getElementById(element);
    var positionInfo = element.getBoundingClientRect();
    var height = positionInfo.height;
    var width = positionInfo.width;
    
    return {'height' : height, 'width' : width};
}


function get_relative_pos(event, element) {
    var size = getSize(element);
    var height = size['height'];
    var width = size['width'];

    var x_y = getCoords(event);
    var click_x = x_y['x'];
    var click_y = x_y['y'];

    var x_relative = click_x / height;
    var y_relative = click_y / width;

    return {"x_relative" : x_relative, "y_relative" : y_relative}
}

function is_in_dist(x_target,y_target, x_lookup, y_lookup, range) {
    let x_range = Math.abs(x_target - x_lookup);
    let y_range = Math.abs(y_target - y_lookup);

    let dist = Math.sqrt(x_range ** 2 + y_range ** 2);

    if (dist < range) {
        return true;
    } else {
        return false;
    }

}

function get_compound(event, element) {
    let compounds = [
        ['Goddard Docks', { 'x' : 0.113, 'y': 0.14 } ],
        ['Blanc Brinery', { 'x' : 0.331, 'y': 0.129 } ],
        ['Lawson Station', { 'x' : 0.463, 'y': 0.251 } ],
        ['Golden Acres', { 'x' : 0.609, 'y': 0.147 } ],
        ["Salter's Pork", { 'x' : 0.825, 'y': 0.19 } ],
        ['Maw Battery', { 'x' : 0.182, 'y': 0.408 } ],
        ['Arden Parish', { 'x' : 0.734, 'y': 0.406 } ],
        ['Iron Works', { 'x' : 0.157, 'y': 0.625 } ],
        ['Fort Carmic', { 'x' : 0.343, 'y': 0.652} ],
        ['Sweetbell Flour', { 'x' : 0.511, 'y': 0.47 } ],
        ['Windy Run', { 'x' : 0.89, 'y': 0.561 } ],
        ['Nicholls Prison', { 'x' : 0.711, 'y': 0.627 } ],
        ['Hemlock And Hide', { 'x' : 0.839, 'y': 0.824 } ],
        ['C&A Lumber', { 'x': 0.656, 'y': 0.799 } ],
        ['Bradley & Cravens Brickworks', { 'x' : 0.424, 'y': 0.854 } ],
        ['Liberty Arsenal', { 'x' : 0.193, 'y': 0.833 } ],
    ]
    var click_relative = get_relative_pos(event, element);
    
    for (var i = 0; i < compounds.length; i++ ) {
        var in_dist = is_in_dist(click_relative["x_relative"], click_relative["y_relative"], compounds[i][1]['x'], compounds[i][1]['y'], 0.1)
        if (in_dist) {
            return compounds[i][0]
        }
    }
    return "None"
}

function get_alert(event, element) {
    let aaa = get_compound(event, element)
    alert (aaa)
    
}