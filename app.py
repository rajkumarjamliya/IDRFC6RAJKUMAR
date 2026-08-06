<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Delhivery - IDRFC6 Dewas Warehouse Hub Management</title>
    <!-- Tailwind CSS for Styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 font-sans text-xs">

    <!-- Top Banner Header -->
    <div class="bg-blue-900 text-white p-3 shadow-md flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <i class="fa-solid fa-truck-fast text-yellow-400 text-3xl"></i>
            <div>
                <h1 class="text-xl font-bold tracking-wider">DELHIVERY – IDRFC6 DEWAS WAREHOUSE HUB</h1>
                <p class="text-xs text-yellow-300">Advanced Piklist, Employee Work & Courier Dispatch Management System</p>
            </div>
        </div>
        <div class="bg-yellow-400 text-blue-950 font-bold px-4 py-2 rounded text-sm shadow">
            Plan By: RAJKUMAR JAMLIYA
        </div>
    </div>

    <!-- Main Content Grid -->
    <div class="p-3 grid grid-cols-1 md:grid-cols-12 gap-3">

        <!-- Sidebar / Main Modules Overview -->
        <div class="md:col-span-3 space-y-3">
            <div class="bg-white p-3 rounded shadow border border-gray-200">
                <h2 class="bg-emerald-800 text-white font-bold p-2 text-center rounded mb-3 text-sm">
                    1. SYSTEM KE MAIN MODULES
                </h2>
                
                <div class="space-y-3">
                    <div class="flex items-start space-x-2 border-b pb-2">
                        <i class="fa-solid fa-house text-blue-600 text-base mt-1"></i>
                        <div>
                            <p class="font-bold text-blue-900">1. HOME & MAIN WORK DATA</p>
                            <p class="text-gray-600">Daily piklist / employee work entry, edit, delete, auto time capture, live work report.</p>
                        </div>
                    </div>

                    <div class="flex items-start space-x-2 border-b pb-2">
                        <i class="fa-solid fa-chart-line text-blue-600 text-base mt-1"></i>
                        <div>
                            <p class="font-bold text-blue-900">2. COURIER & DISPATCH REPORT</p>
                            <p class="text-gray-600">Courier wise manifest, cancel, dispatch, return, pending calculation, timing update.</p>
                        </div>
                    </div>

                    <div class="flex items-start space-x-2 border-b pb-2">
                        <i class="fa-solid fa-users text-blue-600 text-base mt-1"></i>
                        <div>
                            <p class="font-bold text-blue-900">3. EMPLOYEE & COURIER MANAGEMENT</p>
                            <p class="text-gray-600">Employee list, Emp ID management, Courier company list management.</p>
                        </div>
                    </div>

                    <div class="flex items-start space-x-2">
                        <i class="fa-solid fa-trash-can text-blue-600 text-base mt-1"></i>
                        <div>
                            <p class="font-bold text-blue-900">4. ADMIN & RECYCLE BIN</p>
                            <p class="text-gray-600">Admin security, password change, deleted data recovery, trash management.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Middle Column: Work Data Entry & Live Tables -->
        <div class="md:col-span-5 space-y-3">
            <!-- Module 1: Entry Section -->
            <div class="bg-white p-3 rounded shadow border border-gray-200">
                <h2 class="bg-blue-900 text-white font-bold p-1.5 text-center rounded mb-2 text-xs">
                    1. HOME & MAIN WORK DATA (LIVE ENTRY)
                </h2>

                <!-- Live Work Data Entry Form -->
                <div class="bg-blue-50 p-2 rounded border border-blue-200 mb-3">
                    <p class="font-bold text-blue-900 border-b border-blue-200 pb-1 mb-2">Add New Piklist / Employee Task Entry</p>
                    <form id="workEntryForm" class="space-y-2">
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="font-semibold block">Piklist No.</label>
                                <input type="text" id="piklistNo" class="w-full p-1 border rounded" required placeholder="PKL1004">
                            </div>
                            <div>
                                <label class="font-semibold block">Select Employee</label>
                                <select id="empSelect" class="w-full p-1 border rounded" required>
                                    <option value="AJAY PATEL (W222449)">AJAY PATEL (W222449)</option>
                                    <option value="PANKAJ PATEL (W224500)">PANKAJ PATEL (W224500)</option>
                                    <option value="KAMLESH MANDOI (W225396)">KAMLESH MANDOI (W225396)</option>
                                    <option value="ABHISHEK PATEL (W225403)">ABHISHEK PATEL (W225403)</option>
                                </select>
                            </div>
                            <div>
                                <label class="font-semibold block">Task Type</label>
                                <select id="taskType" class="w-full p-1 border rounded" required>
                                    <option value="Picking">Picking</option>
                                    <option value="Packing">Packing</option>
                                    <option value="Scanning">Scanning</option>
                                    <option value="Manifest">Manifest</option>
                                    <option value="Cancel">Cancel</option>
                                    <option value="Return">Return</option>
                                </select>
                            </div>
                            <div>
                                <label class="font-semibold block">Courier Company</label>
                                <select id="courierSelect" class="w-full p-1 border rounded">
                                    <option value="N/A">N/A</option>
                                    <option value="Delhivery">Delhivery</option>
                                    <option value="Shadowfax">Shadowfax</option>
                                    <option value="ATS">ATS</option>
                                    <option value="Xpressbees">Xpressbees</option>
                                    <option value="DTDC">DTDC</option>
                                    <option value="Bluedart">Bluedart</option>
                                    <option value="Ekart">Ekart</option>
                                </select>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-2 items-center">
                            <div>
                                <label class="font-semibold block">Parcel Count</label>
                                <input type="number" id="parcelCount" min="1" value="1" class="w-full p-1 border rounded" required>
                            </div>
                            <div class="text-right pt-3">
                                <button type="submit" class="bg-blue-900 text-white px-4 py-1.5 rounded font-bold hover:bg-blue-800">
                                    Save Entry
                                </button>
                            </div>
                        </div>
                    </form>
                    <p class="text-[10px] text-green-700 font-semibold mt-1">
                        <i class="fa-solid fa-clock"></i> Server / System Time (Automatic): <span id="liveClock"></span>
                    </p>
                </div>

                <!-- Recent Summary & Table -->
                <div class="flex justify-between items-center mb-1">
                    <span class="font-bold text-gray-800">Today's Recorded Entries</span>
                    <button onclick="exportCSV()" class="bg-emerald-700 text-white px-2 py-1 rounded text-[10px] font-bold">
                        Download Work Report (CSV)
                    </button>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse border border-gray-300">
                        <thead class="bg-blue-100 text-blue-900 text-[10px]">
                            <tr>
                                <th class="border p-1">Piklist No</th>
                                <th class="border p-1">Employee Name</th>
                                <th class="border p-1">Task Type</th>
                                <th class="border p-1">Courier</th>
                                <th class="border p-1">Count</th>
                                <th class="border p-1">Time</th>
                            </tr>
                        </thead>
                        <tbody id="workTableBody" class="text-[10px]">
                            <!-- Rows added dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Right Column: Dispatch Report & Admin -->
        <div class="md:col-span-4 space-y-3">
            <!-- Module 2: Dispatch Report -->
            <div class="bg-white p-3 rounded shadow border border-gray-200">
                <h2 class="bg-blue-900 text-white font-bold p-1.5 text-center rounded mb-2 text-xs">
                    2. COURIER & DISPATCH REPORT
                </h2>

                <div class="overflow-x-auto">
                    <table class="w-full text-center border-collapse border border-gray-300">
                        <thead class="bg-blue-900 text-white text-[9px]">
                            <tr>
                                <th class="border p-1">Courier</th>
                                <th class="border p-1">Manifest</th>
                                <th class="border p-1">Cancel</th>
                                <th class="border p-1">Dispatch</th>
                                <th class="border p-1">Return</th>
                                <th class="border p-1">Pending</th>
                            </tr>
                        </thead>
                        <tbody id="courierTableBody" class="text-[10px]">
                            <!-- Dynamic Courier Status -->
                        </tbody>
                    </table>
                </div>

                <!-- Formula Highlight Box -->
                <div class="bg-blue-50 border border-blue-300 p-2 rounded mt-2 text-[10px]">
                    <p class="font-bold text-blue-900">Pending Calculation Formula:</p>
                    <p class="text-gray-700 font-mono">Pending = (Yesterday Pending) + Manifest - Cancel - Dispatch + Return</p>
                </div>
            </div>

            <!-- Module 3 & 4: Admin & Benefits -->
            <div class="bg-white p-3 rounded shadow border border-gray-200 space-y-2">
                <h2 class="bg-orange-600 text-white font-bold p-1 text-center rounded text-xs">
                    SYSTEM KE FAAYDE (BENEFITS)
                </h2>
                <ul class="space-y-1 text-gray-700 text-[10px] grid grid-cols-2 gap-1">
                    <li><i class="fa-solid fa-circle-check text-green-600"></i> Live Data Entry</li>
                    <li><i class="fa-solid fa-circle-check text-green-600"></i> Employee Tracking</li>
                    <li><i class="fa-solid fa-circle-check text-green-600"></i> Courier Manifest</li>
                    <li><i class="fa-solid fa-circle-check text-green-600"></i> 100% Accurate</li>
                    <li><i class="fa-solid fa-circle-check text-green-600"></i> Full Paperless</li>
                    <li><i class="fa-solid fa-circle-check text-green-600"></i> Easy CSV Download</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Bottom Goal Banner -->
    <div class="bg-blue-950 text-white p-2 text-center text-xs font-bold flex justify-around items-center">
        <span>OUR GOAL: Warehouse Work ko Digital, Transparent, Accurate & Live Banana!</span>
        <span class="text-yellow-400">100% Automated | 100% Accurate | 100% Live</span>
    </div>

    <!-- JavaScript Engine -->
    <script>
        // Store Data
        let workEntries = [
            { piklist: "PKL1001", emp: "AJAY PATEL", task: "Picking", courier: "N/A", count: 1, time: "10:15:30 AM" },
            { piklist: "PKL1002", emp: "PANKAJ PATEL", task: "Packing", courier: "N/A", count: 1, time: "10:22:45 AM" },
            { piklist: "PKL1003", emp: "ABHISHEK PATEL", task: "Manifest", courier: "Delhivery", count: 10, time: "10:30:12 AM" }
        ];

        let courierData = [
            { name: "Delhivery", manifest: 15, cancel: 2, dispatch: 12, returnItem: 1, prevPending: 0 },
            { name: "Shadowfax", manifest: 10, cancel: 1, dispatch: 8, returnItem: 0, prevPending: 0 },
            { name: "ATS", manifest: 8, cancel: 0, dispatch: 6, returnItem: 1, prevPending: 0 },
            { name: "Xpressbees", manifest: 12, cancel: 1, dispatch: 9, returnItem: 1, prevPending: 0 },
            { name: "DTDC", manifest: 9, cancel: 0, dispatch: 8, returnItem: 0, prevPending: 0 },
            { name: "Bluedart", manifest: 7, cancel: 1, dispatch: 5, returnItem: 1, prevPending: 0 },
            { name: "Ekart", manifest: 6, cancel: 0, dispatch: 4, returnItem: 0, prevPending: 0 }
        ];

        // Real-Time Clock
        function updateClock() {
            const now = new Date();
            document.getElementById('liveClock').innerText = now.toLocaleTimeString();
        }
        setInterval(updateClock, 1000);
        updateClock();

        // Render Work Entry Table
        function renderWorkTable() {
            const tbody = document.getElementById('workTableBody');
            tbody.innerHTML = '';
            workEntries.forEach(item => {
                tbody.innerHTML += `
                    <tr class="border-b">
                        <td class="p-1 border">${item.piklist}</td>
                        <td class="p-1 border">${item.emp}</td>
                        <td class="p-1 border">${item.task}</td>
                        <td class="p-1 border">${item.courier}</td>
                        <td class="p-1 border font-bold">${item.count}</td>
                        <td class="p-1 border text-gray-500">${item.time}</td>
                    </tr>
                `;
            });
        }

        // Render Courier Report Table
        function renderCourierTable() {
            const tbody = document.getElementById('courierTableBody');
            tbody.innerHTML = '';
            courierData.forEach(c => {
                // Formula: Pending = Yesterday Pending + Manifest - Cancel - Dispatch + Return
                let pending = c.prevPending + c.manifest - c.cancel - c.dispatch + c.returnItem;
                tbody.innerHTML += `
                    <tr class="border-b">
                        <td class="p-1 border font-bold text-left">${c.name}</td>
                        <td class="p-1 border">${c.manifest}</td>
                        <td class="p-1 border text-red-600">${c.cancel}</td>
                        <td class="p-1 border text-green-600">${c.dispatch}</td>
                        <td class="p-1 border">${c.returnItem}</td>
                        <td class="p-1 border font-bold text-blue-900 bg-yellow-50">${pending}</td>
                    </tr>
                `;
            });
        }

        // Form Submit Handler
        document.getElementById('workEntryForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const now = new Date();
            const empFullName = document.getElementById('empSelect').value.split(' (')[0];
            
            const newEntry = {
                piklist: document.getElementById('piklistNo').value,
                emp: empFullName,
                task: document.getElementById('taskType').value,
                courier: document.getElementById('courierSelect').value,
                count: parseInt(document.getElementById('parcelCount').value),
                time: now.toLocaleTimeString()
            };

            workEntries.unshift(newEntry);
            renderWorkTable();
            document.getElementById('workEntryForm').reset();
        });

        // CSV Download Function
        function exportCSV() {
            let csvContent = "data:text/csv;charset=utf-8,Piklist No,Employee,Task Type,Courier,Count,Time\n";
            workEntries.forEach(e => {
                csvContent += `${e.piklist},${e.emp},${e.task},${e.courier},${e.count},${e.time}\n`;
            });
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "Delhivery_Work_Report.csv");
            document.body.appendChild(link);
            link.click();
        }

        // Initial Load
        renderWorkTable();
        renderCourierTable();
    </script>
</body>
</html>
