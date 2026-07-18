import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api';
import { PDFDocument } from 'pdf-lib';

export default function NewOrderWizard() {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState(null);
  const [fileUrl, setFileUrl] = useState(null);
  const [pages, setPages] = useState(0);
  
  const [printType, setPrintType] = useState('single_side');
  const [color, setColor] = useState('black_white');
  const [binding, setBinding] = useState('none');
  const [copies, setCopies] = useState(1);
  const [notes, setNotes] = useState('');
  
  const [costPreview, setCostPreview] = useState(null);
  const [createdOrder, setCreatedOrder] = useState(null);
  
  const [transactionId, setTransactionId] = useState('');
  const [screenshot, setScreenshot] = useState(null);
  const [screenshotUrl, setScreenshotUrl] = useState(null);
  
  const [serviceActive, setServiceActive] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    fetchSettings();
  }, []);

  useEffect(() => {
    if (pages > 0) {
      calculateCost();
    }
  }, [pages, printType, color, binding, copies]);

  const fetchSettings = async () => {
    try {
      const res = await api.get('/public/settings');
      setServiceActive(res.data.service_active ?? true);
    } catch (err) {
      console.error('Failed to fetch settings', err);
    }
  };

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setFileUrl(URL.createObjectURL(selectedFile));
      
      // Count pages client-side for the UI preview
      const arrayBuffer = await selectedFile.arrayBuffer();
      const pdfDoc = await PDFDocument.load(arrayBuffer);
      setPages(pdfDoc.getPageCount());
    } else {
      alert("Please select a valid PDF file.");
    }
  };

  const handleScreenshotChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setScreenshot(selectedFile);
      setScreenshotUrl(URL.createObjectURL(selectedFile));
    }
  };

  const calculateCost = async () => {
    try {
      const res = await api.post(`/orders/calculate-cost?pages=${pages}&copies=${copies}&print_type=${printType}&color=${color}&binding=${binding}`);
      setCostPreview(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const submitOrder = async () => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('print_type', printType);
    formData.append('color', color);
    formData.append('binding', binding);
    formData.append('copies', copies);
    formData.append('notes', notes);

    try {
      const res = await api.post('/orders', formData);
      setCreatedOrder(res.data);
      setStep(4);
    } catch (err) {
      alert("Error submitting order");
    }
  };

  const submitPayment = async () => {
    const formData = new FormData();
    formData.append('payment_transaction_id', transactionId);
    formData.append('screenshot', screenshot);

    try {
      await api.post(`/orders/${createdOrder.id}/payment`, formData);
      alert("Payment submitted successfully!");
      navigate('/student/dashboard');
    } catch (err) {
      alert("Error submitting payment");
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8 border border-gray-200">
      <h1 className="text-2xl font-bold mb-6 text-gray-900">New Print Order</h1>
      
      {!serviceActive && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <p className="text-red-700 font-bold">Service is not available at the moment.</p>
          <p className="text-red-600 mt-1">Contact ARV for further on-demand orders.</p>
        </div>
      )}
      
      {/* Stepper logic */}
      <div className="flex mb-8 items-center justify-between">
        {['Upload PDF', 'Options & Preview', 'Confirm', 'Payment'].map((label, index) => (
          <div key={index} className={`flex-1 text-center font-medium ${step >= index + 1 ? 'text-campus-blue' : 'text-gray-400'}`}>
            <div className={`mx-auto w-8 h-8 rounded-full flex items-center justify-center mb-2 
              ${step >= index + 1 ? 'bg-campus-blue text-white' : 'bg-gray-200 text-gray-500'}`}>
              {index + 1}
            </div>
            {label}
          </div>
        ))}
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <label className={`block border-2 border-dashed rounded-lg p-12 text-center ${!serviceActive ? 'bg-gray-100 border-gray-200 cursor-not-allowed' : 'border-gray-300 cursor-pointer hover:border-campus-blue'}`}>
            <span className="text-gray-500 block mb-2">{!serviceActive ? 'Upload disabled' : 'Click to select PDF'}</span>
            <input type="file" accept="application/pdf" className="hidden" onChange={handleFileChange} disabled={!serviceActive} />
          </label>
          {file && <p className="text-sm text-green-600 font-medium text-center">Selected: {file.name} ({pages} pages)</p>}
          <button disabled={!file} onClick={() => setStep(2)} className="w-full bg-campus-blue text-white py-2 rounded-md disabled:bg-gray-300">Next</button>
        </div>
      )}

      {step === 2 && (
        <div className="grid grid-cols-2 gap-8">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium">Print Type</label>
              <select value={printType} onChange={e => setPrintType(e.target.value)} className="w-full mt-1 border rounded p-2">
                <option value="single_side">Single Sided</option>
                <option value="double_side">Double Sided</option>
                <option value="multi_page">Multiple Pages Per Sheet (2-up)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium">Color</label>
              <select value={color} onChange={e => setColor(e.target.value)} className="w-full mt-1 border rounded p-2">
                <option value="black_white">Black & White</option>
                <option value="color">Color</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium">Binding</label>
              <select value={binding} onChange={e => setBinding(e.target.value)} className="w-full mt-1 border rounded p-2">
                <option value="none">None</option>
                <option value="spiral">Spiral Binding</option>
                <option value="soft">Soft Binding</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium">Copies</label>
              <input type="number" min="1" value={copies} onChange={e => setCopies(Number(e.target.value))} className="w-full mt-1 border rounded p-2" />
            </div>
            <div>
              <label className="block text-sm font-medium">Notes for Operator</label>
              <textarea value={notes} onChange={e => setNotes(e.target.value)} className="w-full mt-1 border rounded p-2"></textarea>
            </div>
            <div className="flex justify-between mt-6">
              <button onClick={() => setStep(1)} className="bg-gray-200 px-4 py-2 rounded-md">Back</button>
              <button onClick={() => setStep(3)} className="bg-campus-blue text-white px-4 py-2 rounded-md">Next</button>
            </div>
          </div>
          <div>
            <div className="h-96 border rounded mb-4 overflow-hidden bg-gray-100">
              <iframe src={fileUrl} className="w-full h-full" title="PDF Preview" />
            </div>
          </div>
        </div>
      )}

      {step === 3 && costPreview && (
        <div className="space-y-6">
          <div className="bg-gray-50 p-6 rounded-lg border text-center">
            <h2 className="text-xl font-bold mb-4">Campus Copies Bill</h2>
            <div className="grid grid-cols-2 gap-4 text-left max-w-sm mx-auto mb-4 text-sm">
              <span className="text-gray-600">Pages:</span> <span className="font-medium text-right">{costPreview.pages}</span>
              <span className="text-gray-600">Copies:</span> <span className="font-medium text-right">{costPreview.copies}</span>
              <span className="text-gray-600">Printing Cost:</span> <span className="font-medium text-right">₹{costPreview.printing_cost.toFixed(2)}</span>
              <span className="text-gray-600">Binding Cost:</span> <span className="font-medium text-right">₹{costPreview.binding_cost.toFixed(2)}</span>
              <span className="text-gray-600">GST:</span> <span className="font-medium text-right">₹{costPreview.gst_amount.toFixed(2)}</span>
            </div>
            <div className="text-2xl font-bold text-campus-blue border-t pt-4 max-w-sm mx-auto">
              Grand Total: ₹{costPreview.grand_total.toFixed(2)}
            </div>
          </div>
          <div className="flex justify-between">
            <button onClick={() => setStep(2)} className="bg-gray-200 px-4 py-2 rounded-md">Back</button>
            <button onClick={submitOrder} className="bg-campus-blue text-white px-8 py-2 rounded-md font-bold">Confirm & Place Order</button>
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="space-y-6 text-center">
          <h2 className="text-xl font-bold">Make Payment</h2>
          <p className="text-gray-600 mb-4">Scan the QR code to pay ₹{createdOrder?.grand_total.toFixed(2)}</p>
          <div className="mx-auto flex flex-col items-center justify-center rounded">
            {costPreview?.qr_code_path ? (
              <img src={`${api.defaults.baseURL}/${costPreview.qr_code_path}`} alt="QR Code" className="w-48 h-48 object-contain border" />
            ) : (
              <div className="w-48 h-48 bg-gray-200 flex items-center justify-center rounded">
                <span className="text-gray-500">QR Code Placeholder</span>
              </div>
            )}
            {costPreview?.upi_id && (
              <p className="mt-2 font-medium text-gray-700">UPI ID: {costPreview.upi_id}</p>
            )}
          </div>
          <div className="max-w-md mx-auto space-y-4 text-left mt-6">
            <div>
              <label className="block text-sm font-medium">Transaction ID</label>
              <input type="text" value={transactionId} onChange={e => setTransactionId(e.target.value)} className="w-full mt-1 border rounded p-2" required />
            </div>
            <div>
              <label className="block text-sm font-medium">Upload Screenshot</label>
              <input type="file" accept="image/*" onChange={handleScreenshotChange} className="w-full mt-1 border rounded p-2" required />
            </div>
            {screenshotUrl && <img src={screenshotUrl} alt="Preview" className="h-32 mx-auto object-cover border" />}
          </div>

          <button disabled={!transactionId || !screenshot} onClick={submitPayment} className="w-full max-w-md bg-green-600 text-white py-2 rounded-md disabled:bg-gray-300 font-bold mt-4">
            Submit Payment for Verification
          </button>
        </div>
      )}
    </div>
  );
}
