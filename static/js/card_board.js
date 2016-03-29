// alert('a')
$(document).ready(function(){

	document.session = $('#session').val();

	websocket = requestBoardStatus()

	$('#join').click(function(e) {
		if ($('#join').text() == 'Join') {
			websocket.send(document.session);
		}
		$.ajax({
			url: '/',
			type: 'POST',
			data: {
				session: document.session,
				player_name : $('#player-name').val()
			},
			dataType: 'html',
			beforeSend: function(xhr, settings) {
				// $(e.target).attr({'disabled': 'disabled'});
			},
			success: function(data, status, xhr){
				if(data == 'full'){
					// 如果人已满，则跳转到棋局
					alert('人满了');
					// window.location.href = '/board_status'
				} else if(data == 'game start!') {
					console.log('游戏开始！');
					$('#join').html('已开始');
				} else{
					$('#card-board').html(data);
					// 加入游戏，将按钮禁用
					$('#join').html('已加入').attr('disabled', true);
					$('input#player-name').attr('disabled', true);
					// requestBoardStatus()
				}
			}
		});
	});


	function requestBoardStatus() {
		var host = 'ws://127.0.0.1:8888/board_status';

		var websocket = new WebSocket(host);

		websocket.onopen = function(e){
			// alert('welcome to the game!');
			// websocket.send(document.session);
		};

		websocket.onmessage = function(e) {
			info = jQuery.parseJSON(e.data);
			// console.log(info);
			if(info['type'] == 'waiting') {
				$('#player-list').append("<li class='list-group-item player-name' name='"+info['playername']+"'>" + info['playername'] + "</li>")
			} else if(info['type'] == 'quited'){
				// console.log($("#player-list .player-name[name="+info['playername']+"]"));
				$("#player-list .player-name[name="+info['playername']+"]").remove();
			} else if(info['type'] == 'started') {
				// 如果是自己的回合，则点亮按钮
				$('#actions button').attr('disabled', true);
				if(info['currentTurn'] == $('#player-name').val()) {
					$('#actions button').attr('disabled', false);
				}
				// $('#player-list').append("<li class='list-group-item player-name'>" + info['playername'] + "</li>")
				$('#own-cards-list').empty()
				// 把自己的牌展示出来
				for (var i = info['cards'].length - 1; i >= 0; i--) {
					$('#own-cards-list').append("<img class='card' src='static/cards/" + info['cards'][i] + ".png' name='" + info['cards'][i] + "'></img >");
				};
				$('#player-list .player-name').attr('class', 'list-group-item disabled player-name');
				// console.log(info['currentTurn']);
				// console.log($("#player-list li[name="+info['currentTurn']+"]"));
				$("#player-list li[name="+info['currentTurn']+"]").attr('class', 'list-group-item player-name');
				// $('#pre-cards').html(info['currentCard']);
				// $('#current-turn').html(info['currentTurn']);
				$('#player-list .player-name span').remove()
				if (info['whoPlayed'] != ''){
					$("#player-list li[name="+info['whoPlayed']+"]").append("<span class='glyphicon glyphicon-thumbs-up' aria-hidden='true'></span>")
				}

				// $('#who-played').html(info['whoPlayed']);
				// 展示所有人上一次打的牌
				$('#played-card').html('');
				for (name in info['played_card_dict']) {
					$('#played-card').append("<div class='row'><button class='btn btn-primary' type='button'>" + name + "<span class='badge'>"+info['remain_cards'][name].length+"</span></button><ul class='cards-list' name='"+name+"'></ul></div>");
					if(info['played_card_dict'][name].length == 0) {
						$('.cards-list[name='+name+']').append("<span>PASS</span>")
					}
					console.log(name);
					console.log(info['played_card_dict'][name].length);
					for(var i = info['played_card_dict'][name].length - 1; i >= 0; i--) {
						card = info['played_card_dict'][name][i]
						$('.cards-list[name='+name+']').append("<img class='card' name="+card+" src='static/cards/"+card+".png'>");
					};
				}
			} else if(info['type'] == 'over') {
				alert('游戏结束');
				$('#played-card').html('');
				for (name in info['remain_cards']) {
					$('#played-card').append("<div class='row'><button class='btn btn-primary' type='button'>" + name + "</button><ul class='cards-list' name='"+name+"'></ul></div>");
					if (info['remain_cards'][name].length == 0) {
						$('.cards-list[name='+name+']').append("<span>WINNER</span>")
					}
					for (var i = info['remain_cards'][name].length - 1; i >= 0; i--) {
						card = info['remain_cards'][name][i]
						$('.cards-list[name='+name+']').append("<img class='card' name="+card+" src='static/cards/"+card+".png'>");
					};
				}
				$('#join').html('重新开始').attr('disabled', false);
				$('#player-list').empty()
				// $('#actions').append("<button type='button' class='btn btn-default' id='restart'>再来一局</button>")
			}	
			// $('#card-board').html(e.data);
		}

		websocket.onerror = function(e){ };

		return websocket
	}

	$( ".container" ).on( "click", "#own-cards .card", function() {
        if ($(this).attr('isSelected') == 'true'){
            $(this).attr('isSelected', 'false')
        }else{
            $(this).attr('isSelected', 'true')
        }
    });

    $( ".container" ).on( "click", "#playCard", function(e) {
        e.preventDefault();
        playerName = $('#player-name').val();
        cards = [];
        $("#own-cards .card[isSelected='true']").each(function(){
            cards.push($(this).attr('name'));
        });
        console.log(cards);
        // url = $('#playCard').attr('url');
        $.ajax({
            url: '/play_card',
            type: 'post',
            dataType: 'html',
            data: {
                'cards': cards,
                'player_name': playerName
            },
        })
        .done(function(msg) {
        	console.log(msg);
           	if(msg == 'illegal') {
           		alert('出牌有误');
           		$("#own-cards .card[isSelected='true']").each(function(){
		            $(this).attr('isSelected', 'false');
		        });
           	}
        })
        .fail(function() {
            console.log("error");
        })
    });

    $( ".container" ).on( "click", "#passTurn", function(e) {
        e.preventDefault();
        playerName = $('#player-name').val();
        cards = [];
        $("#own-cards .card[isSelected='true']").each(function(){
            cards.push($(this).attr('name'));
        });
        console.log(cards);
        // url = $('#playCard').attr('url');
        $.ajax({
            url: '/play_card',
            type: 'post',
            dataType: 'html',
            data: {
                'cards': cards,
                'player_name': playerName
            },
        })
        .done(function(msg) {
        	console.log(msg);
           	if(msg == 'illegal') {
           		alert('出牌有误');
           	}
        })
        .fail(function() {
            console.log("error");
        })
    });


});