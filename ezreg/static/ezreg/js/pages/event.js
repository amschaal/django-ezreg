
angular.module('ezreg')
.controller('PriceController', ['$scope','Price', PriceController])
function PriceController($scope,Price) {
	var defaults={};
	$scope.init = function(params){
		$scope.event_id = params.event_id;
		$scope.prices = Price.query({event:$scope.event_id});
	}
	$scope.addPrice = function(){
		$scope.prices.push(new Price({'event':$scope.event_id}));
	}
	$scope.savePrices = function(){
		
		angular.forEach($scope.prices, function(price, key) {
			var success = function(response){
				console.log('success',response);
			}
			var error = function(response,stuff){
				console.log('error',response,price);
				price.errors = response.data;
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
		});
	}
}