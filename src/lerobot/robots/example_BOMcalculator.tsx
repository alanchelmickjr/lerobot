import React, { useState, useMemo } from 'react';
import { Calculator, Package, AlertCircle, Download, ShoppingCart } from 'lucide-react';

const RobotBOMCalculator = () => {
  const [inventory, setInventory] = useState({
    // SO-ARM101 Components (per arm set: 1 leader + 1 follower)
    'sts3215_12v': 12,  // STS3215 12V 360° (follower & wheels & neck)
    'sts3215_147': 6,  // STS3215 5V 1/147 gear for leader
    'sts3215_191': 4,  // STS3215 5V 1/191 gear for leader
    'sts3215_345_leader': 2,  // STS3215 5V 1/345 gear for leader
    'motor_controller': 4,  // Bus servo adapter boards
    'usb_cable': 4,  // USB A to C cables
    'power_5v': 2,  // 5V 5A+ power supply (leader arm)
    'power_12v': 2,  // 12V 5A+ power supply (follower arm)
    'm2x6_screws': 100,  // M2x6mm screws
    'm3x6_screws': 50,  // M3x6mm screws
    'clamps': 4,  // Clamps for assembly
    'screwdriver_set': 1,  // Precision screwdriver set
    
    // LeKiwi Specific Components
    'raspberry_pi5': 0,  // Raspberry Pi 5
    'omni_wheels': 0,  // Omni wheels
    'pi_case': 0,  // Raspberry Pi case
    'm3x12_screws': 0,  // M3x12 screws
    'm3x16_screws': 0,  // M3x16 screws
    'm3x20_screws': 0,  // M3x20 screws
    'm4x18_screws': 0,  // M4x18 screws
    'base_plates': 0,  // 3D printed base plates
    
    // XLeRobot Specific Components
    'ikea_cart': 0,  // IKEA RÅSKOG cart
    'anker_battery': 0,  // Anker 300Wh battery
    'usbc_cables': 0,  // USB-C to USB-C cables
    'camera_wrist': 0,  // Wrist RGB cameras
    'camera_head': 0,  // Head depth camera
  });

  const bomRequirements = {
    'SO-ARM101': {
      description: 'One complete arm set (1 leader + 1 follower)',
      parts: {
        'sts3215_12v': 6,
        'sts3215_147': 3,
        'sts3215_191': 2,
        'sts3215_345_leader': 1,
        'motor_controller': 2,
        'usb_cable': 2,
        'power_5v': 1,
        'power_12v': 1,
        'm2x6_screws': 48,
        'm3x6_screws': 24,
        'clamps': 2,
        'screwdriver_set': 1,
      }
    },
    'LeKiwi': {
      description: 'Mobile manipulator (includes 1x SO-ARM101)',
      parts: {
        'SO-ARM101': 1,
        'sts3215_12v': 3,  // Additional 3x for wheels
        'raspberry_pi5': 1,
        'omni_wheels': 3,
        'pi_case': 1,
        'm3x12_screws': 12,
        'm3x16_screws': 21,
        'm3x20_screws': 4,
        'm4x18_screws': 27,
        'base_plates': 1,
        'motor_controller': 1,
        'power_12v': 1,
      }
    },
    'XLeRobot': {
      description: 'Dual-arm mobile robot (includes 1x LeKiwi + 1x SO-ARM101)',
      parts: {
        'LeKiwi': 1,
        'SO-ARM101': 1,
        'sts3215_12v': 2,  // Additional 2x for neck
        'ikea_cart': 1,
        'anker_battery': 1,
        'usbc_cables': 3,
        'camera_wrist': 2,
        'camera_head': 1,
      }
    }
  };

  const partNames = {
    'sts3215_12v': 'STS3215 12V 360° (Follower/Wheels/Neck)',
    'sts3215_147': 'STS3215 5V 1/147 gear (Leader)',
    'sts3215_191': 'STS3215 5V 1/191 gear (Leader)',
    'sts3215_345_leader': 'STS3215 5V 1/345 gear (Leader)',
    'motor_controller': 'Bus Servo Adapter Board',
    'usb_cable': 'USB-A to USB-C Cable',
    'power_5v': '5V 5A+ Power Supply (Leader)',
    'power_12v': '12V 5A+ Power Supply (Follower)',
    'm2x6_screws': 'M2x6mm Screws',
    'm3x6_screws': 'M3x6mm Screws',
    'm3x12_screws': 'M3x12mm Screws',
    'm3x16_screws': 'M3x16mm Screws',
    'm3x20_screws': 'M3x20mm Screws',
    'm4x18_screws': 'M4x18mm Screws',
    'clamps': 'Assembly Clamps',
    'screwdriver_set': 'Precision Screwdriver Set',
    'raspberry_pi5': 'Raspberry Pi 5',
    'omni_wheels': 'Omni Wheels',
    'pi_case': 'Raspberry Pi Case',
    'base_plates': '3D Printed Base Plates',
    'ikea_cart': 'IKEA RÅSKOG Cart',
    'anker_battery': 'Anker 300Wh Battery',
    'usbc_cables': 'USB-C to USB-C Cable',
    'camera_wrist': 'Wrist RGB Camera',
    'camera_head': 'Head Depth Camera',
  };

  const calculateMaxBuildable = (productName) => {
    const requirements = bomRequirements[productName].parts;
    let maxBuildable = Infinity;
    let limitingPart = null;

    const expandedInventory = { ...inventory };

    const expandRequirements = (reqs, mult = 1) => {
      const expanded = {};
      Object.entries(reqs).forEach(([part, qty]) => {
        if (bomRequirements[part]) {
          const subExpanded = expandRequirements(bomRequirements[part].parts, qty * mult);
          Object.entries(subExpanded).forEach(([subPart, subQty]) => {
            expanded[subPart] = (expanded[subPart] || 0) + subQty;
          });
        } else {
          expanded[part] = (expanded[part] || 0) + (qty * mult);
        }
      });
      return expanded;
    };

    const expandedReqs = expandRequirements(requirements);

    Object.entries(expandedReqs).forEach(([part, qtyNeeded]) => {
      const available = expandedInventory[part] || 0;
      const possible = Math.floor(available / qtyNeeded);
      if (possible < maxBuildable) {
        maxBuildable = possible;
        limitingPart = part;
      }
    });

    return { max: maxBuildable === Infinity ? 0 : maxBuildable, limiting: limitingPart, requirements: expandedReqs };
  };

  const buildableResults = useMemo(() => ({
    'SO-ARM101': calculateMaxBuildable('SO-ARM101'),
    'LeKiwi': calculateMaxBuildable('LeKiwi'),
    'XLeRobot': calculateMaxBuildable('XLeRobot'),
  }), [inventory]);

  const handleInventoryChange = (part, value) => {
    const numValue = Math.max(0, parseInt(value) || 0);
    setInventory(prev => ({
      ...prev,
      [part]: numValue
    }));
  };

  const downloadInventorySheet = () => {
    let csv = 'Part Name,Part Code,Current Inventory,SO-ARM101 Needs,LeKiwi Needs,XLeRobot Needs\n';
    
    Object.keys(inventory).forEach(partCode => {
      const currentQty = inventory[partCode];
      const so101Qty = buildableResults['SO-ARM101'].requirements[partCode] || 0;
      const lekiwiQty = buildableResults['LeKiwi'].requirements[partCode] || 0;
      const xleQty = buildableResults['XLeRobot'].requirements[partCode] || 0;
      
      csv += `"${partNames[partCode]}","${partCode}",${currentQty},${so101Qty},${lekiwiQty},${xleQty}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'robot_bom_inventory.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const downloadOrderSheet = () => {
    let csv = 'Part Name,Part Code,Current Stock,Need to Order,Priority\n';
    const allLimitingParts = new Set();
    
    Object.values(buildableResults).forEach(result => {
      if (result.limiting) {
        allLimitingParts.add(result.limiting);
      }
    });

    Object.entries(buildableResults).forEach(([product, result]) => {
      Object.entries(result.requirements).forEach(([part, needed]) => {
        const current = inventory[part] || 0;
        if (current < needed) {
          const shortage = needed - current;
          const priority = allLimitingParts.has(part) ? 'HIGH' : 'MEDIUM';
          csv += `"${partNames[part]}","${part}",${current},${shortage},${priority}\n`;
        }
      });
    });

    if (csv.split('\n').length <= 2) {
      alert('No parts needed! You have enough inventory to build everything.');
      return;
    }

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'robot_order_sheet.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Calculator className="w-10 h-10 text-indigo-600" />
              <div>
                <h1 className="text-4xl font-bold text-gray-800">Robot BOM Calculator</h1>
                <p className="text-gray-600">SO-ARM101, LeKiwi & XLeRobot Build Planner</p>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={downloadInventorySheet}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors shadow-md"
              >
                <Download className="w-5 h-5" />
                Download Inventory
              </button>
              <button
                onClick={downloadOrderSheet}
                className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors shadow-md"
              >
                <ShoppingCart className="w-5 h-5" />
                Create Order Sheet
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-8">
            {Object.entries(buildableResults).map(([name, result]) => {
              const servo12vNeeded = name === 'SO-ARM101' ? 6 : name === 'LeKiwi' ? 9 : 17;
              return (
                <div key={name} className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-6 border-2 border-indigo-200">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xl font-bold text-gray-800">{name}</h3>
                    <Package className="w-8 h-8 text-indigo-600" />
                  </div>
                  <div className="text-5xl font-bold text-indigo-600 mb-2">{result.max}</div>
                  <p className="text-sm text-gray-600 mb-2">{bomRequirements[name].description}</p>
                  <p className="text-xs text-indigo-700 font-semibold mb-3">Needs {servo12vNeeded}x 12V servos</p>
                  {result.limiting && result.max < 1 && (
                    <div className="flex items-start gap-2 text-xs text-amber-700 bg-amber-50 p-2 rounded">
                      <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                      <span>Limited by: {partNames[result.limiting]}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Inventory Management</h2>
          
          <div className="space-y-8">
            <section>
              <h3 className="text-xl font-bold text-indigo-600 mb-4 pb-2 border-b-2 border-indigo-200">SO-ARM101 Components</h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {['sts3215_12v', 'sts3215_147', 'sts3215_191', 'sts3215_345_leader', 'motor_controller', 'usb_cable', 'power_5v', 'power_12v', 'm2x6_screws', 'm3x6_screws', 'clamps', 'screwdriver_set'].map(part => (
                  <div key={part} className="bg-gray-50 rounded-lg p-4">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      {partNames[part]}
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={inventory[part]}
                      onChange={(e) => handleInventoryChange(part, e.target.value)}
                      className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
                    />
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="text-xl font-bold text-green-600 mb-4 pb-2 border-b-2 border-green-200">LeKiwi Specific Parts</h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {['raspberry_pi5', 'omni_wheels', 'pi_case', 'm3x12_screws', 'm3x16_screws', 'm3x20_screws', 'm4x18_screws', 'base_plates'].map(part => (
                  <div key={part} className="bg-gray-50 rounded-lg p-4">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      {partNames[part]}
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={inventory[part]}
                      onChange={(e) => handleInventoryChange(part, e.target.value)}
                      className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 transition-all"
                    />
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="text-xl font-bold text-purple-600 mb-4 pb-2 border-b-2 border-purple-200">XLeRobot Specific Parts</h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {['ikea_cart', 'anker_battery', 'usbc_cables', 'camera_wrist', 'camera_head'].map(part => (
                  <div key={part} className="bg-gray-50 rounded-lg p-4">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      {partNames[part]}
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={inventory[part]}
                      onChange={(e) => handleInventoryChange(part, e.target.value)}
                      className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                    />
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="mt-8 p-6 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl">
            <h3 className="text-lg font-bold text-gray-800 mb-3">Build Requirements Summary</h3>
            {Object.entries(buildableResults).map(([name, result]) => (
              <div key={name} className="mb-4">
                <h4 className="font-bold text-indigo-600 mb-2">{name} - Full Parts Breakdown:</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 text-sm">
                  {Object.entries(result.requirements).map(([part, qty]) => (
                    <div key={part} className={`p-2 rounded ${inventory[part] >= qty ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      <div className="font-semibold">{partNames[part]}</div>
                      <div>{inventory[part] || 0} / {qty}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-8 text-center text-gray-600 text-sm">
          <p>🤖 Calculator combines BOMs from SO-ARM100, LeKiwi, and XLeRobot projects</p>
          <p className="mt-2">⚡ STS3215 12V 360° servos are used for follower arms, wheels, AND 2-DOF neck (all interchangeable)</p>
          <p className="mt-1">💡 Leader arms use 5V servos (gear ratios: 1/147, 1/191, 1/345)</p>
          <p className="mt-1">📦 Updates live as you type! Download sheets to Excel for ordering.</p>
        </div>
      </div>
    </div>
  );
};

export default RobotBOMCalculator;