var x_calendar = function(element, options){
    this.element = element;
    // this.enabledDay = options.enabledDay;
    this.enabledDay = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31];
    this.viewDay = options.viewDay || new Date();
    this.year = this.viewDay.getFullYear();
    this.month = this.viewDay.getMonth();
    this.monthArr = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    this.getCalendar();
    this.bindEvent();
}
x_calendar.prototype = {
    getCalendar: function(){

        var isLeapYear = (((this.year % 4 === 0) && (this.year % 100 !== 0)) || (this.year % 400 === 0));   
        var daysInMonth = [31, (isLeapYear ? 29 : 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][this.month]

        var dateFirst = new Date(this.year+'/'+(this.month+1)+'/'+1);
        var dateLast = new Date(this.year+'/'+(this.month+1)+'/'+daysInMonth);
        var dayFirst = dateFirst.getDay();
        var dayLast = dateLast.getDay();

        var calendar = [];
        for (var i = dayFirst-1; i >= 0; i--) {
            calendar.push('');
        };
        for (var i = 1; i <= daysInMonth; i++) {
            calendar.push(i);
        };
        for (var i = dayLast+1; i < 7; i++) {
            calendar.push('');
        };

        var tbody = '';
        for (var i = 0; i < calendar.length; i++) {
            if(i%7 == 0){
                tbody += '<tr> <td class="'+( ($.inArray(calendar[i], this.enabledDay) == -1)? '':'enabled' )+'" id="'+ calendar[i] +'">'+calendar[i]+'</td>';
            } else if(i%7 == 6){
                tbody += '<td class="'+( ($.inArray(calendar[i], this.enabledDay) == -1)? '':'enabled' )+'" id="'+ calendar[i] +'">'+calendar[i]+'</td> </tr>';
            } else {
                tbody += '<td class="'+( ($.inArray(calendar[i], this.enabledDay) == -1)? '':'enabled' )+'" id="'+ calendar[i] +'">'+calendar[i]+'</td>';
                // <td class="enabled" id="'+ calendar[i] +'">'+calendar[i]+'</td>
            }
        };

        var monthTab = '<ul>';
        for (var i = 0; i < this.monthArr.length; i++) {
            monthTab += '<li value="'+i+'" class="'+(i==1? 'border-top1':'')+'">'+this.monthArr[i]+'</li>';
        };
        monthTab += '</ul>';

        var thead = 
        '<thead>'+
            '<tr id="month-year">'+
                '<th><div class="left"></div></th>'+
                '<th colspan="2" class="month" month="'+(this.month+1)+'">'+this.monthArr[this.month]+monthTab+'</th>'+
                '<th colspan="3" class="year" year="'+this.year+'">'+this.year+'</th>'+
                '<th><div class="right"></div></th>'+
            '</tr>'+
            '<tr class="week">'+
                '<th>Mon</th>'+
                '<th>Tue</th>'+
                '<th>Wed</th>'+
                '<th>Thr</th>'+
                '<th>Fri</th>'+
                '<th>Sat</th>'+
                '<th>Sun</th>'+
            '</tr>'+
        '</thead>';
        var table = '<table class="x-calendar" cellspacing="0">'+thead+'<tbody id="calendar_body">'+tbody+'</tbody></table>';
        this.element.html(table);
    },
    bindEvent: function(){
        var that = this;
        this.element.on('click', '.left', function(){
            that.month--;
            if(that.month == -1){
                that.month = 11;
                that.year--;
                if(that.year == 1900){
                    that.year++;
                    that.month++;
                }
            }
            that.getCalendar();
            that.element.trigger({
                type: 'changeMonth',
                month: parseInt(that.month)+1,
                year: parseInt(that.year)
            })
        })
        this.element.on('click', '.right', function(){
            that.month++;
            if(that.month == 12){
                that.month = 0;
                that.year++;
            }
            that.getCalendar();
            that.element.trigger({
                type: 'changeMonth',
                month: parseInt(that.month)+1,
                year: parseInt(that.year)
            })
        })
        this.element.on('click', '.month', function(){
            $(this).find('ul').toggle();
            // $(this).toggleClass('show');
        })
        this.element.on('click', '.month li', function(){
            var value = $(this).attr('value');
            that.month = value;
            that.getCalendar();
            that.element.trigger({
                type: 'changeMonth',
                month: parseInt(that.month)+1,
                year: parseInt(that.year)
            })
        })
        this.element.on('click', '.enabled', function(){
            that.element.trigger({
                
                type: 'changeDate',
                date: $(this).html(),
                // date: ($(this).html().lenght === 1 ? '0'+$(this).html() : $(this).html()) ,
                // date: $(this).html().lenght,
                month: parseInt(that.month)+1,
                year: parseInt(that.year),
                elem: this
            })
        })
    }

}
$.fn.x_calendar = function(options, operate){
    if(operate == 'update'){
        var calend = $(this).data('x_calendar');
        calend.enabledDay = options.enabledDay;
        calend.viewDay = options.viewDay || new Date();
        calend.year = calend.viewDay.getFullYear();
        calend.month = calend.viewDay.getMonth();
        calend.getCalendar();
    } else {
        var calend = new x_calendar(this, options);
        $(this).data('x_calendar', calend);
    }
    
    return this;
}