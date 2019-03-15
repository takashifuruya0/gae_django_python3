var TARGET_ELEMENT_ID = '#wordcloud'; // 描画先
if (window.innerWidth > 768) {
  var h = 500;
  var w = 1000;
}else{
  var h = 400;
  var w = 500;
}

function draw_cards(data_ajax){
    //CARDS and MODALS
    var cards = d3.select('#photo-cards')
    cards.selectAll('div').remove()
    for (sample of data_ajax.samples){  // 配列のfor文はof
      do_on_click = function(prop, val){
          var res = "$('#" + sample.id + "').modal('hide');update_photo_by_sidebar('"
              + prop + "', '" + val + "')"
          return res
      }
      // CARDS
      cards
        .append('div')
          .attr("class", "col-4 col-md-3 col-lg-2 photo-card") // style using semantic ui
        .append('div')
          .attr("class", "card")
        .append('img')
//          .attr("src", "/static/"+sample.path_resized_480)
          .attr("src", sample.url_resized_480)
          .attr("width", "100%")
          .attr("data-toggle", "modal")
          .attr("data-target", "#"+sample.id)
      // MODALS
      var modal = cards
        .append("div")
          .attr("class", "modal fade")
          .attr("id", sample.id)
          .attr("tabindex", "-1")
          .attr("role", "dialog")
          .attr("aria-labelledby", "order")
          .attr("aria-hidden", "true")
        .append("div")
          .attr("class", "modal-dialog modal-lg")
          .attr("role", "document")
        .append("div")
          .attr("class", "modal-content")
      // header
      var header = modal.append("div")
        .attr("class", "modal-header")
      var title = header.append('h5')
        .attr("class", "modal-title")
      if (sample.landmark){
        title.html(sample.landmark)
      }else{
        title.html(sample.sitename)
      }
      header.append('button')
        .attr("type", "button")
        .attr("class", "close")
        .attr("data-dismiss", "modal")
        .attr("aria-label", "Close")
        .append("span")
          .attr("aria-hidden", "true")
          .html("&times;")
      // body
      var body = modal.append("div")
        .attr("class", "modal-body")
      // img
      body.append('img')
//        .attr("src", "/static/" + sample.path_resized_1200)
        .attr("src", sample.url_resized_1200)
        .attr("width", "100%")
      // table
      var table = body.append("table").attr("class", "table")
      var tr0 = table.append("tr")
      // country
      tr0.append('th').html('<i class="fas fa-tags"></i> Tags ')
      var td0 = tr0.append('td').append('h5')
      td0.append('span')
        .attr("class", "badge badge-pill badge-warning")
        .attr("onclick", do_on_click('country', sample.country))
        .text(sample.country)
      td0.append('span')
        .attr("class", "badge badge-pill badge-warning")
        .attr("onclick", do_on_click('prefecture', sample.prefecture))
        .text(sample.prefecture)
      td0.append('span')
        .attr("class", "badge badge-pill badge-warning")
        .attr("onclick", do_on_click('sitename', sample.sitename))
        .text(sample.sitename)
      td0.append('span')
        .attr("class", "badge badge-pill badge-warning")
        .attr("onclick", do_on_click('country_en', sample.country_en))
        .text(sample.country_en)
      td0.append('span')
        .attr("class", "badge badge-pill badge-warning")
        .attr("onclick", do_on_click('locality', sample.locality))
        .text(sample.locality)
      td0.append('span')
        .attr("class", "badge badge-pill badge-warning")
        .attr("onclick", do_on_click('landmark', sample.landmark))
        .text(sample.landmark)
      // landmark/location detected by VisionAPI
      if (sample.landmark){
          var tr3 = table.append("tr")
          tr3.append("th").html('<i class="fas fa-landmark"></i> Landmark')
          tr3.append("td").text(sample.landmark)
          var tr4 = table.append("tr")
          tr4.append("th").html('<i class="fas fa-map-marker-alt"></i> Location')
          tr4.append("td").text(
              "(" + sample.location.latitude + ", " + sample.location.longitude + ")"
          )
      }
      // footer
      var footer = modal.append("div")
        .attr("class", "modal-footer")
        .append('a')
          .attr('class', 'btn btn-primary')
          .attr('href', '/photo/detail/'+sample.id)
          .html('<i class="fas fa-info-circle"></i> Detail')
    }
    // LABEL
    d3.selectAll('.ajax_label').text(data_ajax.label)
}

function draw_wc(data){
  var random = d3.randomIrwinHall(2); // アーウィンホール分布
  var countMax = d3.max(data, function(d){ return d.count} );
  var sizeScale = d3.scaleLinear().domain([0, countMax]).range([10, 100])

  var words = data.map(function(d) {
    return {
    url: d.url,
    text: d.word,
    property: d.property,
    size: sizeScale(d.count) //頻出カウントを文字サイズに反映
    };
  });
  d3.layout.cloud().size([w, h])
    .words(words)
    .rotate(function() { return (~~(Math.random() * 6) - 3) * 30; })
    .font("Impact")
    .fontSize(function(d) { return d.size; })
    .on("end", draw) //描画関数の読み込み
    .start();
  return words;

  // wordcloud 描画
  function draw(words) {
    d3.select(TARGET_ELEMENT_ID)
      .append("svg")
        .attr("class", "ui fluid image") // style using semantic ui
        .attr("viewBox", "0 0 " + w + " " + h )  // ViewBox : x, y, width, height
        .attr("width", "100%")    // 表示サイズの設定
        .attr("height", "100%")   // 表示サイズの設定
      .append("g")
        .attr("transform", "translate(" + w / 2 + "," + h / 2 + ")")
      .selectAll("text")
        .data(words)
      .enter().append("text")
        .style("font-size", function(d) { return d.size + "px"; })
        .style("font-family", "Impact")
        .style("fill", function(d, i) { return d3.schemeCategory10[i % 10]; })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.text; })
        .on("click", function (d){
          // ajax
          $.ajax({
            url: "/ajax/",  // "{% url 'ra:ajax' %}",
            method: "GET",
            data: {
              text: d.text,
              prop: d.property,
            },
            timeout: 10000,
            dataType: "json",
            //リクエストが完了するまで実行される
            beforeSend: function(){
              $('#overlay').removeClass('hide');
            }
          })
          .done(function(data_ajax) {
            // sidebar
            update_sidebar(data_ajax)
            // card
            draw_cards(data_ajax)
            // Word Cloud
            d3.select(TARGET_ELEMENT_ID).select('svg').remove();
            var words = draw_wc(data_ajax.wordcloud_list);
            // overlay
            $('#overlay').addClass('hide');
          })
          .fail(function(){$('#overlay').addClass('hide');})
        });
  }
}

window.onload = function(){
  // ajax
  $.ajax({
    url: "/ajax/",  // "{% url 'ra:ajax' %}",
    method: "GET",
    timeout: 10000,
    dataType: "json",
    //リクエストが完了するまで実行される
    beforeSend: function(){
      $('#overlay').removeClass('hide');
    }
  })
  .done(function(data_ajax) {
    // sidebar
    update_sidebar(data_ajax)
    // card
    draw_cards(data_ajax)
    // word cloud
    var words = draw_wc(data_ajax.wordcloud_list)
    // overlay
    $('#overlay').addClass('hide');
  })
  .fail(function(){$('#overlay').addClass('hide');})
}

var update_photo_by_sidebar = function (prop, text) {
    // ajax
  $.ajax({
    url: "/ajax/",  // "{% url 'ra:ajax' %}",
    method: "GET",
    data: {
      text: text,
      prop: prop,
    },
    timeout: 10000,
    dataType: "json",
    //リクエストが完了するまで実行される
    beforeSend: function(){
      $('#overlay').removeClass('hide');
    }
  })
  .done(function(data_ajax) {
    // card
    draw_cards(data_ajax)
    // sidebar
    update_sidebar(data_ajax)
    // word cloud
    var words = draw_wc(data_ajax.wordcloud_list)

    // overlay
    d3.select(TARGET_ELEMENT_ID).select('svg').remove();
    $('#overlay').addClass('hide');
  })
  .fail(function(){$('#overlay').addClass('hide');})
}

// sidebarのupdate
var update_sidebar = function (data_ajax) {
    // country
    var ul_country = d3.select('#countrySubmenu')
    ul_country.selectAll('li').remove()
    for (sample of data_ajax.property_list.country) {  // 配列のfor文はof
        if (sample.count > 0){
            ul_country.append('li').append('a')
                .attr("onclick", "update_photo_by_sidebar('" + sample.property +"', '" + sample.word + "')")
                .html(sample.word + '<span class="badge badge-pill badge-light" style="color:black;">' + sample.count + '</span>')
        }
    }
    // country_en
    var ul_country_en = d3.select('#countryEnSubmenu')
    ul_country_en.selectAll('li').remove()
    for (sample of data_ajax.property_list.country_en) {  // 配列のfor文はof
        if (sample.count > 0){
            ul_country_en.append('li').append('a')
                .attr("onclick", "update_photo_by_sidebar('" + sample.property +"', '" + sample.word + "')")
                .html(sample.word + '<span class="badge badge-pill badge-light" style="color:black;">' + sample.count + '</span>')
        }
    }
    // landmark
    var ul_landmark = d3.select('#landmarkSubmenu')
    ul_landmark.selectAll('li').remove()
    for (sample of data_ajax.property_list.landmark) {  // 配列のfor文はof
        if (sample.count > 0){
            ul_landmark.append('li').append('a')
                .attr("onclick", "update_photo_by_sidebar('" + sample.property +"', '" + sample.word + "')")
                .html(sample.word + '<span class="badge badge-pill badge-light" style="color:black;">' + sample.count + '</span>')
        }
    }
    // locality
    var ul_locality = d3.select('#localitySubmenu')
    ul_locality.selectAll('li').remove()
    for (sample of data_ajax.property_list.locality) {  // 配列のfor文はof
        if (sample.count > 0){
            ul_locality.append('li').append('a')
                .attr("onclick", "update_photo_by_sidebar('" + sample.property +"', '" + sample.word + "')")
                .html(sample.word + '<span class="badge badge-pill badge-light" style="color:black;">' + sample.count + '</span>')
        }
    }
    // prefecture
    var ul_prefecture = d3.select('#prefectureSubmenu')
    ul_prefecture.selectAll('li').remove()
    for (sample of data_ajax.property_list.prefecture) {  // 配列のfor文はof
        if (sample.count > 0){
            ul_prefecture.append('li').append('a')
                .attr("onclick", "update_photo_by_sidebar('" + sample.property +"', '" + sample.word + "')")
                .html(sample.word + '<span class="badge badge-pill badge-light" style="color:black;">' + sample.count + '</span>')
        }
    }
    // sitename
    var ul_sitename = d3.select('#sitenameSubmenu')
    ul_sitename.selectAll('li').remove()
    for (sample of data_ajax.property_list.sitename) {  // 配列のfor文はof
        if (sample.count > 0){
            ul_sitename.append('li').append('a')
                .attr("onclick", "update_photo_by_sidebar('" + sample.property +"', '" + sample.word + "')")
                .html(sample.word + '<span class="badge badge-pill badge-light" style="color:black;">' + sample.count + '</span>')
        }
    }
}