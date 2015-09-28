var app = angular.module('ezreg');
app.requires.push('ngTable');
app.controller('RegistrationController', ['$scope','$http','$modal','growl','Registration',"NgTableParams", RegistrationController])

function RegistrationController($scope,$http,$modal,growl,Registration,NgTableParams) {
	var defaults={};
	console.log('wtf');
	
//	var registrations = Registration.query({event: '2Z89K20AZ3'});
	$scope.tableParams = new NgTableParams({
//	      page: 1, // show first page
	      count: 10 // count per page
	    }, {
	      filterDelay: 0,
//	      dataset: registrations
		  	getData: function(params) {
		  		var url = params.url();
		  		console.log(params);
		  		console.log(url);
		  	var query_params = {page:url.page,page_size:url.count,ordering:params.orderBy().join(',').replace('+','')};
		  	angular.extend(query_params, params.filter());
	        // ajax request to api
		  	return $http.get('/api/registrations/',{params:query_params}).then(function(response){
		  		console.log(response.data);
		  		params.total(response.data.count);
		  		return response.data.results;
		  	});
//	        return Registration.query({event: '2Z89K20AZ3',page_size:3}).$promise.then(function(data) {
//	          console.log(data,data.length);
////	          params.total(data.count); // recal. page nav controls
//	          return data;
//	        });
	      }
	    });
//	getData: function(params) {
//        // ajax request to api
//        return Registration.query({event: '2Z89K20AZ3').$promise.then(function(data) {
//          params.total(data.inlineCount); // recal. page nav controls
//          return data.results;
//        });
//      }
		$scope.getSelected = function(){
			var emails = [];
			angular.forEach($scope.checked,function(value,key){
				if (value)
					emails.push(key);
			});
			return emails;
		}
		$scope.update_statuses_old = function(){
			console.log($scope.getSelected());
		};
		$scope.update_statuses = function () {

		    var modalInstance = $modal.open({
		      animation: $scope.animationsEnabled,
		      templateUrl: 'updateStatus.html',
		      controller: 'updateStatusCtrl',
		      size: 'lg',
		      resolve: {
		        selected: function () {
		          return $scope.getSelected();
		        }
		      }
		    });

		    modalInstance.result.then(function () {
		    	console.log('refresh');
		    }, function () {
		      $log.info('Modal dismissed at: ' + new Date());
		    });
		  };
}


app.controller('updateStatusCtrl', function ($scope, $modalInstance, selected) {

	  $scope.selected = selected;

	  $scope.ok = function () {
	    $modalInstance.close($scope.selected);
	  };

	  $scope.cancel = function () {
	    $modalInstance.dismiss('cancel');
	  };
	});


$(document).ready(function() {
    // Setup - add a text input to each footer cell
    $('#registrations tfoot th.searchable').each( function () {
        var title = $('#example thead th').eq( $(this).index() ).text();
        $(this).html( '<input type="text" class="search-box" placeholder="Search '+title+'" />' );
    } );
 
    // DataTable
    var table = $('#registrations').DataTable();
 
    // Apply the search
    table.columns().every( function () {
        var that = this;
 
        $( 'input', this.footer() ).on( 'keyup change', function () {
            if ( that.search() !== this.value ) {
                that
                    .search( this.value )
                    .draw();
            }
        } );
    } );
    table.columns([4]).every( function () {
        var column = this;
        var select = $('<select><option value=""></option></select>')
            .appendTo( $(column.footer()).empty() )
            .on( 'change', function () {
                var val = $.fn.dataTable.util.escapeRegex(
                    $(this).val()
                );

                column
                    .search( val ? '^'+val+'$' : '', true, false )
                    .draw();
            } );

        column.data().unique().sort().each( function ( d, j ) {
            select.append( '<option value="'+d+'">'+d+'</option>' )
        } );
    } );
    $('#registrations tbody').on( 'click', 'tr', function () {
        $(this).toggleClass('selected');
    } );
    $('#updateStatusesButton').click( function () {
        console.log( table.rows('.selected').data());
    } );
} );
