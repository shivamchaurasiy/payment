

from django.shortcuts import render
from .forms import PaymentForm
from .models import ItemModel

# Create your views here.
import razorpay
from django.views.decorators.csrf import csrf_exempt

def item_payment(request):
    if request.method=="POST":
        name = request.POST['name']
        amount = int(request.POST['amount']) * 100
        client = razorpay.Client(auth=("rzp_test_Xlv4T6HwO79lfY" , "L63ZkPI36zVW8H6TssVP6bcA" ))
        response_payment = client.order.create({'amount':amount, 'currency':'INR',
                              'payment_capture':'1' })
    
        print(response_payment)
        order_status = response_payment['status']
        order_id = response_payment['id']
        
        if order_status=='created':
            product = ItemModel(name=name , amount =amount , order_id = response_payment['id'],)
            product.save()
            response_payment['name'] = name
            fm = PaymentForm( request.POST or None)
            return render(request,'app/item_payment.html',{'form':fm,'payment':response_payment})

    fm = PaymentForm()
    return render(request,'app/item_payment.html',{'form':fm})

@csrf_exempt
def payment_status(request):
    # print(request.POST)
    if request.method=='POST':
        response = request.POST
        print(response)
        params_dict = {
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature']
        }

        # client instance
        client = razorpay.Client(auth=("rzp_test_Xlv4T6HwO79lfY" , "L63ZkPI36zVW8H6TssVP6bcA" ))

        try:
            status = client.utility.verify_payment_signature(params_dict)
            item = ItemModel.objects.get(order_id=response['razorpay_order_id'])
            item.razorpay_payment_id = response['razorpay_payment_id']
            item.paid = True
            item.save()
            return render(request, 'app/payment_status.html', {'status': True})
        except:
            return render(request, 'app/payment_status.html', {'status': False})
    return render(request, 'app/payment_status.html')
