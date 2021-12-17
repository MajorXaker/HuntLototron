function blah() {
    return 5;
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

var aaa = is_in_dist(0.3,0.3,0.46, 0.25,0.01)

