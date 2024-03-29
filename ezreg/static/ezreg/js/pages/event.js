
var app = angular.module('ezreg');
app.requires.push('ui.tinymce');
app.controller('PriceController', ['$scope','$http','growl','Price','PaymentProcessor', PriceController])
.controller('EventPageController', ['$scope','$http','growl','EventPage', EventPageController])
.controller('EventTextController', ['$scope','$http','growl','Event', EventTextController])

function PriceController($scope,$http,growl,Price,PaymentProcessor) {
	var defaults={};
	var event_processors_url = null;
	var errorMessageHandler = function(response){
		growl.error(response.data.error ,{ttl: 5000});
	};
	$scope.today = (new Date()).toISOString().slice(0, 10);
	$scope.tzoffset = (new Date()).getTimezoneOffset() * 60000; //offset in milliseconds
	$scope.selected_processors={};
	$scope.init = function(params){
		$scope.event_id = params.event_id;
		$scope.organizer = params.organizer;
		event_processors_url = params.event_processors_url;
		$scope.prices = Price.query({event:$scope.event_id,page_size:100});
		$scope.processors = PaymentProcessor.query({organizer:$scope.organizer});
		$http.get(event_processors_url).then(function(response){
			$scope.selected_processors = response.data.processors;
		});
	}
	$scope.addPrice = function(){
		$scope.prices.push(new Price({'event':$scope.event_id}));
	}
	$scope.savePrices = function(){
		
		angular.forEach($scope.prices, function(price, key) {
			var success = function(response){
				growl.success("Price '"+price.name+"' saved.",{ttl: 5000});
			}
			var error = function(response,stuff){
				price.errors = response.data;
				growl.error("Price '"+price.name+"' not saved.",{ttl: 5000});
			}
			
			if (price.id)
				price.$save(success,error);
			else
				price.$create(success,error);
		});
	}
	$scope.deletePrice = function(price,index){
		if(!price.id){
			$scope.prices.splice(index,1);
			return;
		}
		if(!confirm('Are you sure you want to delete this price?'))
			return;
		price.$delete(function(){
				$scope.prices.splice(index,1);
			},
			function(){
				growl.error("Deleting price failed.  It may be referenced by existing registrations.",{ttl: 5000});
			});
	}
	$scope.saveProcessors = function(){
		$http.post(event_processors_url,{'processors':$scope.selected_processors}).then(
				function(response){
					growl.success("Payment processors updated",{ttl: 5000});
				},
				function(response){growl.error("Saving payment processors failed.",{ttl: 5000});}
		);
	}
	$scope.isActive = function(price) {
	    if (price.disable)
	       return false;
	    var start_date = price.start_date && price.start_date.toISOString ? (new Date(price.start_date - $scope.tzoffset)).toISOString().slice(0, 10): price.start_date;
	    var end_date = price.end_date && price.end_date.toISOString ? (new Date(price.end_date - $scope.tzoffset)).toISOString().slice(0, 10): price.end_date;
	    if (start_date && $scope.today < start_date)
	       return false;
	    if (end_date && $scope.today > end_date)
           return false;
        return true;
	}
}

function EventPageController($scope,$http,growl,EventPage) {
	//$scope.tinymceOptions = {'foobar':'baz'};
	var errorMessageHandler = function(response){
		growl.error(response.data.error ,{ttl: 5000});
	}
	$scope.init = function(params){
		$scope.event_id = params.event_id;
		$scope.getPages();
		$scope.$watchCollection('pages', function(pages) {
			console.log('pages', pages);
		});
	}
	$scope.getPages = function(){
	    $scope.pages = EventPage.query({event:$scope.event_id});
	}
	$scope.addPage = function(){
		$scope.pages.push(new EventPage({event:$scope.event_id,heading:'New page',page_size:100}));
	}
	$scope.savePage = function(page){
		if (page.id)
			page.$save(function(){
				growl.success("Page saved",{ttl: 5000});
			},function(response){
				growl.error('Unable to save page.  Please ensure that all fields are filled out.' ,{ttl: 5000});
			});
		else
			page.$create(function(){
				growl.success("Page created",{ttl: 5000});
			},function(response){
				growl.error('Unable to create page.  Please ensure that all fields are filled out.' ,{ttl: 5000});
			});
	}
	$scope.deletePage = function(page,index){
		if(!confirm('Are you sure you want to delete this page?'))
			return;
		if(!page.id){
			$scope.pages.splice(index,1);
			growl.success("Page deleted",{ttl: 5000});
			return;
		}
		page.$delete(function(){
			growl.success("Page deleted",{ttl: 5000});
			$scope.pages.splice(index,1);
		},function(response){
			growl.error('Unable to delete page.' ,{ttl: 5000});
		});
	}

}

function EventTextController($scope,$http,growl,Event) {
	$scope.init = function(params){
		$scope.event_id = params.event_id;
		$scope.config = params.config;
		$scope.event = Event.get({id:$scope.event_id});
	}	
	$scope.save = function(){
		$http.patch('/api/events/'+$scope.event_id+'/',{'config':$scope.event.config})
		.then(function(greeting) {
			growl.success("Custom texts updated.",{ttl: 5000});
		}, function(reason) {
			growl.error("Unable to update custom texts.",{ttl: 5000});
		});
	}

}