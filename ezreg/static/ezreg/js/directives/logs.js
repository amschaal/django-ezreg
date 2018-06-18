
angular.module("django-logger", ['ui.bootstrap'])
.directive('logModal', function($modal,DRFNgTableParams) {
	return {
		restrict: 'AE',
		templateUrl: 'template/django-logger/modal-button.html',
		scope: {
			objectId:'=',
			contentType:'='
		},
		controller: function ($scope,$rootScope) {
			$scope.openModal = function(){
				var modalInstance = $modal.open({
				      templateUrl: 'template/django-logger/modal.html',
				      controller: 'LogModalController',
				      size: 'lg',
				      resolve: {
				        objectId: function () {
				          return $scope.objectId;
				        },
						contentType: function () {
						  return $scope.contentType;
						}
				      }
				    });

//				    modalInstance.result.then(function (selectedItem) {
//				      $scope.selected = selectedItem;
//				    }, function () {
//				      $log.info('Modal dismissed at: ' + new Date());
//				    });
			}
		}
	}
});
angular.module("django-logger").directive('logs', function($modal,DRFNgTableParams) {
	return {
		restrict: 'AE',
		templateUrl: 'template/django-logger/logs.html',
		scope: {
			objectId:'=',
			contentType:'='
		},
		controller: function ($scope,$rootScope) {
			$scope.tableParams = DRFNgTableParams('/api/logs/',{sorting: {  },filter:{}});
		}
	}
});

angular.module("django-logger").directive('logTable', ['DRFNgTableParams',function(DRFNgTableParams) {
    return {
        restrict: 'AE',
        replace: true,
        scope: {
            contentType: '=',  
            objectId: '=',  //field in model to be changed
            url:'@'  //api url
        },
        template: '<div><button ng-click="tableParams.reload()" class="btn btn-sm pull-right">Refresh</button>\
        			<table ng-table="tableParams" show-filter="true" class="table table-bordered table-striped table-condensed">\
				  	      <tr ng-repeat="row in $data track by row.id">\
				        <td data-title="\'Created\'" sortable="\'created\'">{[row.created | date: \'short\']}</td>\
				        <td data-title="\'Text\'" sortable="\'text\'" filter="{text__icontains: \'text\'}" >{[row.text]}</td>\
				      </tr>\
				    </table></div>',
    	controller: function($scope){
    		$scope.url = $scope.url || '/api/logs/';
    		var tableSettings = {sorting: { created: "desc" },filter:{content_type:$scope.contentType,object_id:$scope.objectId}};
    		$scope.tableParams = DRFNgTableParams('/api/logs/',tableSettings);
    		$scope.$watch('objectId', function(newValue, oldValue) {
    			angular.extend($scope.tableParams.filter(), {'object_id':newValue});
  			});
    		$scope.$watch('contentType', function(newValue, oldValue) {
    			angular.extend($scope.tableParams.filter(), {'content_type':newValue});
  			});
    	}
    };
}])

angular.module("django-logger").controller('LogModalController', function ($scope, $modalInstance, objectId, contentType) {

	  $scope.objectId = objectId;
	  $scope.contentType = contentType;
	  $scope.close = function () {
		  $modalInstance.dismiss();//$modalInstance.close();
	  };
});


angular.module("django-logger").run(['$templateCache', function($templateCache) {
	$templateCache.put('template/django-logger/modal-button.html',
		'<a ng-click="openModal()">Test</a>'
	);
}]);

angular.module("django-logger").run(['$templateCache', function($templateCache) {
	$templateCache.put('template/django-logger/modal.html',
	'<div class="modal-header"><h3 class="modal-title">Title</h3></div>\
			<div class="modal-body"><log-table content-type="contentType" object-id="objectId"></log-table></div>\
			<div class="modal-footer"><button class="btn btn-primary" ng-click="close()">Close</button></div>'
	);
}]);
