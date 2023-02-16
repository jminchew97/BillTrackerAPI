let isInEditMode = false;
  async function getJson(url)
  {
    let response = await fetch(url);
    let data = await response.json();
    return data;
  }



  async function main()
  {

    jdata = await getJson("http://127.0.0.1:5000/bill");
    // fill out each column and row
    for (let i = 0; i < jdata.length; i++)
    {
      let bill = jdata[i]

      // calculate date differences
      const oneDay = 24 * 60 * 60 * 1000;
      let todays_date = new Date();
      let due_date = Date.parse(bill['due_date']);

      var days_left = Math.round(Math.abs((due_date - todays_date) / oneDay));
    

      document.getElementById("table-rows").innerHTML +=
              `<tr id="${i}" data-bill-uuid="${bill.id}"><th scope="row"><text>${i}</text></th>` +
              `<td ><text id="name${i}" class="editField${i}"> ${bill.name} </text> </td>` +
              `<td ><text id="amount${i}" class="editField${i}">${bill.amount}</text> </td>` +
              `<td> ${days_left}</td>` +
              `<td ><text id="due_date${i}" class="editField${i}">${bill.due_date}</text></td>` +
              `<td><button id="editBtn${i}" data-row-id="${i}" onclick="clickedEditButton(this)" type="button" class="btn btn-outline-secondary"> <i class="fa fa-pencil-square-o" aria-hidden="true"></i></button></td></tr>`


    }

    // add "create" row at bottom of all rows
    document.getElementById("table-rows").innerHTML +=
              `<tr id="create-row" ><th scope="row"><text>new</text></th>` +
              `<td ><input id="create-name" placeholder="bill name" ></input> </td>` +
              `<td ><input id="create-amount" placeholder="amount" ></input> </td>` +
              `<td> Calculate days left here</td>` +
              `<td ><input id="create-date" type="date" placeholder="day due" ></input></td>` +
              `<td><button id="create-button" type="button" class="btn btn-outline-success"> create</button></td></tr>`

    document.getElementById("create-button").addEventListener("click",postBillToAPI, false);
    

  }
  main();
  function createJsonFromFormData(){

    billData = {
    "name":document.getElementById("create-name").value,
        "amount":document.getElementById("create-amount").value,
        "due_date":document.getElementById("create-date").value
    };
    return billData;
}
  function postBillToAPI(event){
    event.preventDefault();
    let jdata = createJsonFromFormData();
    if (isInEditMode)
    {
      return alert("Must cancel edit before you can do any other action.");
    }
    fetch('http://127.0.0.1:5000/bill', {
        method: 'POST',
        headers: {
            accept: 'application.json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jdata),
        cache: 'default'
    }).then(resp =>
    {
      if (resp.ok)
      {
        return resp.json().then(jdata=> console.log(jdata)).then(() => {window.location.reload() })
      }
      else 
      {
        return resp.json().then((jdata)=> {
          alert(jdata["message"]);
        });
      }
    })
}
  function clickedEditButton(element)
  {
    id = element.getAttribute("data-row-id");
    console.log("getting id=>"+id);

    if (isInEditMode)
    {
      return alert("already in edit mode");
    }
    isInEditMode = true;

    const rowId = id;
    console.log("Row id working ->"+rowId);
    // get corresponding bill object
    let bill = jdata[rowId];

    // get the row by using rowId
    //const row = document.getElementById(rowId);

    console.log("rowID = "+rowId);
    // get all elements that allow editing by user
    let editFields = document.getElementsByClassName("editField" + rowId);

    // convert text fields into input fields
    replaceElementsWithNewElements(editFields, createInputElementsFromTextElements(editFields, rowId));

    //Add check button next to edit button
    let editBtn = document.getElementById("editBtn"+rowId); // get the edit button for the row being edited
    console.log("editBtn"+rowId);

    // create save edit button
    let saveEdit = document.createElement("button");
    let deleteButton = document.createElement("button");
    let cancelButton = document.createElement("button");

    let checkMarkIcon = document.createElement("i");
    checkMarkIcon.setAttribute("class", "fa fa-check");

    // set inner text for delete btn/cancel btn
    deleteButton.textContent = "delete";
    cancelButton.textContent = "cancel";

    // set attributes for buttons
    setAttributes(saveEdit, {"class":"btn btn-success","id":"saveBtn"+rowId , "data-row-id":rowId});
    setAttributes(deleteButton, {"class":"btn btn-danger", "data-row-id":rowId});
    setAttributes(cancelButton, {"class":"btn btn-danger"});
    //Append icon to button
    saveEdit.appendChild(checkMarkIcon);

    // add listeners
    saveEdit.addEventListener("click", serializeFormJson, false);
    deleteButton.addEventListener("click", deleteBill, false);
    // replace edit button with other buttons
    editBtn.replaceWith(saveEdit,deleteButton,cancelButton);



  }
  function createInputElementsFromTextElements(fields, rowId)
  {
    let inputElements = [];
    for (let i =0; i < fields.length; i++)
    {
      let currentTextField = fields[i];

      let input = document.createElement("input");

      input.setAttribute("id", currentTextField.id);

      if (currentTextField.id.includes("amount"))
      {
        input.setAttribute("type","number");
        input.setAttribute("min","0");
      }
      else if (currentTextField.id.includes("date"))
      {
        input.setAttribute("type","date");
      }
      input.setAttribute("placeholder", currentTextField.innerHTML);


      //currentTextField.replaceWith(input);
      input.setAttribute("class", currentTextField.getAttribute("class"));
      inputElements.push(input);

    }
    return inputElements;
  }

  function replaceElementsWithNewElements(oldElements, newElements)
  {
    const oldElementsLen = oldElements.length;

    for (let i =0; i< oldElements.length; i++)
    {
      oldElements[i].replaceWith(newElements[i]);
      console.log("old elements len:" + oldElements.length +"  newElements len: "+ newElements.length);

    }
  }

  function serializeFormJson(event)
  {

    event.preventDefault();
   
    let jdata = {}
    let element = event.currentTarget;
    let rowId =  element.getAttribute("data-row-id");

    let row = document.getElementById(rowId);

    let inputElements = row.getElementsByClassName("editField"+ rowId);
    


    for(let i =0; i< inputElements.length; i++)
    {
      let currentElement = inputElements[i];

      // remove UID from the element id i.e name0 -> name
      let key = currentElement.getAttribute("id").replace(/[0-9]/g, '');
      let defaultValue = currentElement.getAttribute("placeholder");
      let value = currentElement.value;
      console.log(value)
      if (value == "")
      {
        
        jdata[key] = defaultValue;

      }
      else
      {
        console.log("EVERYTHING IS FINE")
        jdata[key] = value;
      }
      

    }
    
    const requestOptions = {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body:JSON.stringify(jdata)
    };
    fetch('http://127.0.0.1:5000/bill/' + getBillUUID(rowId), requestOptions)
            .then(response => {
              if (response.ok) {
                response.json().then(() => {window.location.reload()} )
              }
              else 
              {
                return response.json().then((jdata)=> {
          alert(jdata["message"]);
        });
              }
            })

  }
  function getBillUUID(rowId)
  {
    return document.getElementById(rowId).getAttribute("data-bill-uuid");
  }
  function submitEditToApi(event)
  {
  jdata = serializeFormJson(event);
  }

  function setAttributes(element, attributes)
  {
    for (var key in attributes)
    {
      element.setAttribute(key, attributes[key]);
    }
  }
  function deleteBill(event)
  {
    
    event.preventDefault();
 
    
    

    let element = event.currentTarget;
    let rowId =  element.getAttribute("data-row-id");
    let nameOfBill = document.getElementById("name"+rowId).getAttribute("placeholder");

    console.log(nameOfBill);

    if (!confirm("You are attempting to delete the bill: " + nameOfBill + ". Press 'ok' to confirm. Press 'cancel' to stop. "))
    {
      return 0;
    }

    const requestOptions = {
      method: 'DELETE'
    };
    fetch('http://127.0.0.1:5000/bill/' + getBillUUID(rowId), requestOptions)
            .then(response => response.json())
            .then(data => console.log("deleted")).then(() => {window.location.reload()});

  }
  