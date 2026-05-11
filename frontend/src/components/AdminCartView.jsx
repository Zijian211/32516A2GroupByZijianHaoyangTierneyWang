import { useEffect, useState } from "react";
import { fetchAdminCartsApi } from "../services/api";

function formatCurrency(amount) {
  return `$${Number(amount || 0).toLocaleString("en-AU", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function formatDate(value) {
  if (!value) return "N/A";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "N/A";
  return date.toLocaleDateString("en-AU");
}

function AdminCartView({ currentUser }) {
  const [users, setUsers] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [summary, setSummary] = useState({
    total_users: 0,
    total_cart_items: 0,
    total_cart_value: 0,
    total_order_value: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadAdminData = async () => {
      if (currentUser?.role !== "admin") {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const data = await fetchAdminCartsApi();

        const loadedUsers = data.users || [];
        setUsers(loadedUsers);
        setSummary({
          total_users: data.total_users || loadedUsers.length,
          total_cart_items: data.total_cart_items || 0,
          total_cart_value: data.total_cart_value || 0,
          total_order_value: data.total_order_value || 0,
        });

        if (loadedUsers.length > 0) {
          setSelectedUserId(loadedUsers[0].user_id);
        }
      } catch (err) {
        setError(err.message || "Failed to load admin data.");
      } finally {
        setLoading(false);
      }
    };

    loadAdminData();
  }, [currentUser]);

  if (currentUser?.role !== "admin") {
    return (
      <div className="max-w-2xl mx-auto mt-16 bg-white border border-red-100 rounded-2xl shadow-sm p-10 text-center">
        <div className="text-5xl mb-4">🔒</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Access denied</h2>
        <p className="text-gray-500">Admin users only.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-10 text-center">
        <div className="w-10 h-10 border-4 border-orange-200 border-t-orange-600 rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600 font-medium">Loading admin data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-red-100 p-10 text-center">
        <div className="text-5xl mb-4">⚠️</div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Something went wrong</h2>
        <p className="text-red-600 mb-5">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="bg-red-600 text-white px-5 py-2 rounded-full font-bold hover:bg-red-500 transition"
        >
          Retry
        </button>
      </div>
    );
  }

  const selectedUser = users.find((user) => user.user_id === selectedUserId);

  const selectedCartItems = selectedUser?.cart?.items || [];
  const selectedOrders = selectedUser?.orders || [];

  const selectedCartTotal = selectedUser?.cart?.total_value || 0;

  return (
    <section>
      <div className="mb-8">
        <p className="text-sm font-bold text-orange-600 uppercase tracking-wide mb-2">
          Admin Dashboard
        </p>
        <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900">
          User Cart & Order Lookup
        </h1>
        <p className="text-gray-500 mt-2">
          Click a user ID to view that user's shopping cart and order history.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <p className="text-sm text-gray-500 mb-1">Total Users</p>
          <p className="text-3xl font-extrabold text-gray-900">
            {summary.total_users}
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <p className="text-sm text-gray-500 mb-1">Total Cart Items</p>
          <p className="text-3xl font-extrabold text-blue-800">
            {summary.total_cart_items}
          </p>
        </div>

        <div className="bg-gradient-to-r from-orange-500 to-red-600 rounded-2xl shadow-sm p-6 text-white">
          <p className="text-sm opacity-90 mb-1">Total Order Value</p>
          <p className="text-3xl font-extrabold">
            {formatCurrency(summary.total_order_value)}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <aside className="lg:col-span-1 bg-white rounded-2xl shadow-sm border border-gray-100 p-5 h-fit">
          <h2 className="text-lg font-extrabold text-gray-900 mb-4">Users</h2>

          {users.length === 0 ? (
            <p className="text-sm text-gray-500">No regular users found.</p>
          ) : (
            <div className="space-y-3">
              {users.map((user) => {
                const isSelected = user.user_id === selectedUserId;

                return (
                  <button
                    key={user.user_id}
                    onClick={() => setSelectedUserId(user.user_id)}
                    className={`w-full text-left rounded-xl border p-4 transition ${
                      isSelected
                        ? "border-orange-500 bg-orange-50 shadow-sm"
                        : "border-gray-100 bg-white hover:bg-gray-50"
                    }`}
                  >
                    <p className="text-sm text-gray-500">User ID</p>
                    <p className="font-extrabold text-gray-900 break-all">
                      {user.user_id}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">{user.username}</p>
                    <p className="text-xs text-gray-400 truncate">{user.email}</p>
                  </button>
                );
              })}
            </div>
          )}
        </aside>

        <div className="lg:col-span-3 space-y-6">
          {!selectedUser ? (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-10 text-center">
              <div className="text-5xl mb-4">👤</div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                No user selected
              </h2>
              <p className="text-gray-500">
                Please select a user ID from the list.
              </p>
            </div>
          ) : (
            <>
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Selected User</p>
                    <h2 className="text-2xl font-extrabold text-gray-900">
                      {selectedUser.username}
                    </h2>
                    <p className="text-gray-600 break-all">
                      User ID: {selectedUser.user_id}
                    </p>
                    <p className="text-sm text-gray-400">{selectedUser.email}</p>
                  </div>

                  <div className="bg-orange-50 border border-orange-100 px-5 py-4 rounded-xl">
                    <p className="text-xs text-gray-500 font-medium">
                      Current Cart Total
                    </p>
                    <p className="text-2xl font-extrabold text-orange-600">
                      {formatCurrency(selectedCartTotal)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-6 border-b border-gray-100 bg-gray-50">
                  <h2 className="text-xl font-extrabold text-gray-900">
                    Shopping Cart
                  </h2>
                  <p className="text-sm text-gray-500">
                    Current cart items for this user.
                  </p>
                </div>

                {selectedCartItems.length === 0 ? (
                  <div className="p-10 text-center text-gray-500">
                    <div className="text-5xl mb-4">🧺</div>
                    <p className="font-medium">
                      This user has no items in their cart.
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="text-sm text-gray-500 border-b border-gray-100">
                          <th className="px-6 py-4 font-bold">Item</th>
                          <th className="px-6 py-4 font-bold">Quantity</th>
                          <th className="px-6 py-4 font-bold">Price</th>
                          <th className="px-6 py-4 font-bold">Subtotal</th>
                        </tr>
                      </thead>

                      <tbody>
                        {selectedCartItems.map((item, index) => (
                          <tr
                            key={`${item.product_id || item.name}-${index}`}
                            className="border-b border-gray-100 last:border-b-0 hover:bg-orange-50 transition"
                          >
                            <td className="px-6 py-4 font-semibold text-gray-900">
                              {item.name}
                            </td>
                            <td className="px-6 py-4">
                              <span className="inline-flex items-center justify-center min-w-8 px-3 py-1 rounded-full bg-blue-100 text-blue-800 font-bold">
                                {item.quantity}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-gray-700">
                              {formatCurrency(item.price)}
                            </td>
                            <td className="px-6 py-4 font-bold text-gray-900">
                              {formatCurrency(item.subtotal || item.price * item.quantity)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-6 border-b border-gray-100 bg-gray-50">
                  <h2 className="text-xl font-extrabold text-gray-900">
                    Order History
                  </h2>
                  <p className="text-sm text-gray-500">
                    Previous orders placed by this user.
                  </p>
                </div>

                {selectedOrders.length === 0 ? (
                  <div className="p-10 text-center text-gray-500">
                    <div className="text-5xl mb-4">📦</div>
                    <p className="font-medium">
                      This user has no order history.
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="text-sm text-gray-500 border-b border-gray-100">
                          <th className="px-6 py-4 font-bold">Order ID</th>
                          <th className="px-6 py-4 font-bold">Date</th>
                          <th className="px-6 py-4 font-bold">Status</th>
                          <th className="px-6 py-4 font-bold">Total</th>
                        </tr>
                      </thead>

                      <tbody>
                        {selectedOrders.map((order) => (
                          <tr
                            key={order._id}
                            className="border-b border-gray-100 last:border-b-0 hover:bg-green-50 transition"
                          >
                            <td className="px-6 py-4 font-semibold text-gray-900">
                              {order._id}
                            </td>
                            <td className="px-6 py-4 text-gray-700">
                              {formatDate(order.created_at)}
                            </td>
                            <td className="px-6 py-4">
                              <span className="inline-flex px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
                                {order.status || "Completed"}
                              </span>
                            </td>
                            <td className="px-6 py-4 font-bold text-gray-900">
                              {formatCurrency(order.total_price)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}

export default AdminCartView;