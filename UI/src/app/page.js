'use client';
import { fetchEventSource } from "@microsoft/fetch-event-source";

export default function Home() {

  const addToastr = (message, successfully = true) => {
    const notification = document.createElement("div");
    notification.innerText = message;
    notification.className = "fixed top-4 right-4 text-white p-2 rounded shadow-lg " + (successfully ? "bg-green-500" : "bg-red-500");
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.remove();
    }, 3000);
  }


  const handleSave = async () => {
    const inputValue = document.getElementById("inputField").value;
    document.getElementById("inputField").value = "";
    addToastr(`Saving...`);

    console.log("Sending post request to Api3...");
    await fetchEventSource("http://localhost:8080/update-product", {
      method: "POST",
      headers: {
        "accept": "text/event-stream",
        "content-type": "application/json"
      },
      body: JSON.stringify({
        product_id: 123,
        description: inputValue
      }),
      onmessage(event) {
        console.log(event.data);
        addToastr(event.data);
      },
      onerror(err) {
        console.error("ServerSentEvent error:", err);
        addToastr("Error receiving updates", false);
      }
    });
   };

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <h1 className="text-6xl">Hello from UI!</h1>
        <ol className="list-inside list-decimal text-sm text-center sm:text-left font-[family-name:var(--font-geist-mono)]">
          <li>Get started by saving.</li>
          <li>The UI will send a post to the Api.</li>
          <li>Listen Server-Sent Event to handle the response.</li>
        </ol>
        <div className="flex flex-col gap-4 items-center">
          <input
            id="inputField"
            type="text"
            className="border border-gray-300 rounded px-4 py-2 text-black"
            placeholder="Enter text"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSave();
              }
            }}
          />
          <button
            onClick={handleSave}
            className="rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5"
          >
            Save
          </button>
        </div>
      </main>
    </div>
  );
}
