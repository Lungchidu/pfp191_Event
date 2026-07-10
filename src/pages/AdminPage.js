import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE, isAdmin, TOKEN_KEY } from "../config/auth";
import "./AdminPage.css"; // We will create this simple CSS file

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState("products");
  
  if (!isAdmin()) {
    return (
      <div className="admin-forbidden">
        <h2>Không có quyền truy cập</h2>
        <p>Bạn cần đăng nhập bằng tài khoản admin để xem trang này.</p>
      </div>
    );
  }

  return (
    <div className="admin-container">
      <h1>Bảng Điều Khiển Admin</h1>
      <div className="admin-tabs">
        <button className={activeTab === "products" ? "active" : ""} onClick={() => setActiveTab("products")}>Quản lý Sản Phẩm</button>
        <button className={activeTab === "reviews" ? "active" : ""} onClick={() => setActiveTab("reviews")}>Quản lý Bình Luận</button>
        <button className={activeTab === "test_orders" ? "active" : ""} onClick={() => setActiveTab("test_orders")}>Tạo Đơn Hàng Test</button>
      </div>
      
      <div className="admin-content">
        {activeTab === "products" && <AdminProducts />}
        {activeTab === "reviews" && <AdminReviews />}
        {activeTab === "test_orders" && <AdminTestOrders />}
      </div>
    </div>
  );
}

// ----------------------------------------------------
// PRODUCT MANAGEMENT
// ----------------------------------------------------
function AdminProducts() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [editingProduct, setEditingProduct] = useState(null);
  
  // Form State
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    price: "",
    originalPrice: "",
    stock: "",
    location: "",
    categoryId: 1,
    image: ""
  });
  const [imageFile, setImageFile] = useState(null);

  const fetchProducts = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/products`);
      const data = await res.json();
      if (data.success) setProducts(data.products);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleEdit = (p) => {
    setEditingProduct(p.id);
    setFormData({
      name: p.name,
      description: p.description,
      price: p.price,
      originalPrice: p.originalPrice,
      stock: p.stock,
      location: p.location,
      categoryId: p.categoryId,
      image: p.image
    });
    setImageFile(null);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setImageFile(e.target.files[0]);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Xóa sản phẩm này?")) return;
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      const res = await fetch(`${API_BASE}/api/admin/products/${id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const data = await res.json();
      if (data.success) {
        alert("Đã xóa sản phẩm");
        fetchProducts();
      } else {
        alert(data.message);
      }
    } catch (e) {
      alert("Lỗi");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = editingProduct 
      ? `${API_BASE}/api/admin/products/${editingProduct}`
      : `${API_BASE}/api/admin/products`;
    const method = editingProduct ? "PUT" : "POST";
    const token = localStorage.getItem(TOKEN_KEY);

    const payload = new FormData();
    payload.append("name", formData.name);
    payload.append("description", formData.description);
    payload.append("price", formData.price);
    payload.append("originalPrice", formData.originalPrice);
    payload.append("stock", formData.stock);
    payload.append("location", formData.location);
    payload.append("categoryId", formData.categoryId);
    payload.append("image", formData.image);
    if (imageFile) {
      payload.append("image_file", imageFile);
    }

    try {
      const res = await fetch(url, {
        method,
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: payload
      });
      const data = await res.json();
      if (data.success) {
        alert(data.message);
        setEditingProduct(null);
        setFormData({ name: "", description: "", price: "", originalPrice: "", stock: "", location: "", categoryId: 1, image: "" });
        setImageFile(null);
        fetchProducts();
        navigate("/");
      } else {
        alert(data.message);
      }
    } catch (e) {
      alert("Lỗi");
    }
  };

  return (
    <div>
      <h2>{editingProduct ? "Sửa Sản Phẩm" : "Thêm Sản Phẩm Mới"}</h2>
      <form className="admin-form" onSubmit={handleSubmit}>
        <input name="name" placeholder="Tên sản phẩm" value={formData.name} onChange={handleChange} required />
        <textarea name="description" placeholder="Mô tả" value={formData.description} onChange={handleChange} required />
        <input name="price" type="number" placeholder="Giá" value={formData.price} onChange={handleChange} required />
        <input name="originalPrice" type="number" placeholder="Giá gốc" value={formData.originalPrice} onChange={handleChange} />
        <input name="stock" type="number" placeholder="Số lượng (stock)" value={formData.stock} onChange={handleChange} required />
        <input name="location" placeholder="Địa chỉ" value={formData.location} onChange={handleChange} required />
        <input name="image" placeholder="URL hình ảnh (nếu có)" value={formData.image} onChange={handleChange} />
        <div>
          <label style={{fontSize: "14px", fontWeight: "bold", marginRight: "10px"}}>Hoặc tải ảnh lên:</label>
          <input type="file" name="image_file" accept="image/*" onChange={handleFileChange} />
        </div>
        
        <div style={{marginTop: 10}}>
          <button type="submit">{editingProduct ? "Lưu Thay Đổi" : "Thêm Sản Phẩm"}</button>
          {editingProduct && <button type="button" onClick={() => { setEditingProduct(null); setFormData({ name: "", description: "", price: "", originalPrice: "", stock: "", location: "", categoryId: 1, image: "" })}}>Hủy Sửa</button>}
        </div>
      </form>

      <h3>Danh Sách Sản Phẩm</h3>
      <table className="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tên</th>
            <th>Giá</th>
            <th>Số Lượng</th>
            <th>Hành động</th>
          </tr>
        </thead>
        <tbody>
          {products.map(p => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td>{p.name}</td>
              <td>{p.price}</td>
              <td>{p.stock}</td>
              <td>
                <button onClick={() => handleEdit(p)}>Sửa</button>
                <button onClick={() => handleDelete(p.id)} style={{color: "red"}}>Xóa</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ----------------------------------------------------
// REVIEW MANAGEMENT
// ----------------------------------------------------
function AdminReviews() {
  const [productId, setProductId] = useState("");
  const [reviews, setReviews] = useState([]);

  const fetchReviews = async () => {
    if (!productId) return;
    try {
      const res = await fetch(`${API_BASE}/api/products/${productId}/reviews`);
      const data = await res.json();
      if (data.success) {
        setReviews(data.reviews);
      } else {
        alert(data.message);
      }
    } catch (e) {
      alert("Lỗi khi tải bình luận");
    }
  };

  const handleDelete = async (reviewId) => {
    if (!window.confirm("Xóa bình luận này?")) return;
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      const res = await fetch(`${API_BASE}/api/admin/reviews/${reviewId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      });
      const data = await res.json();
      if (data.success) {
        alert("Đã xóa bình luận");
        fetchReviews();
      } else {
        alert(data.message);
      }
    } catch (e) {
      alert("Lỗi");
    }
  };

  return (
    <div>
      <h2>Quản Lý Bình Luận</h2>
      <div style={{marginBottom: 20}}>
        <input 
          placeholder="Nhập Product ID để xem bình luận" 
          value={productId} 
          onChange={(e) => setProductId(e.target.value)} 
          type="number" 
          style={{padding: 8}}
        />
        <button onClick={fetchReviews} style={{marginLeft: 10, padding: 8}}>Xem</button>
      </div>
      
      <table className="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Người Dùng</th>
            <th>Rating</th>
            <th>Nội Dung</th>
            <th>Hành Động</th>
          </tr>
        </thead>
        <tbody>
          {reviews.map(r => (
            <tr key={r.id}>
              <td>{r.id}</td>
              <td>{r.username}</td>
              <td>{r.rating} ⭐</td>
              <td>{r.comment}</td>
              <td>
                <button onClick={() => handleDelete(r.id)} style={{color: "red"}}>Xóa</button>
              </td>
            </tr>
          ))}
          {reviews.length === 0 && <tr><td colSpan="5">Không có bình luận</td></tr>}
        </tbody>
      </table>
    </div>
  );
}

// ----------------------------------------------------
// TEST ORDER MANAGEMENT
// ----------------------------------------------------
function AdminTestOrders() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    buyer: "admin",
    total: 100000,
    note: "Test order",
    deliveryDate: ""
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      const res = await fetch(`${API_BASE}/api/admin/test-order`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (data.success) {
        alert(`Tạo đơn thành công! Mã đơn: ${data.order_id}`);
        navigate("/");
      } else {
        alert(data.message);
      }
    } catch (e) {
      alert("Lỗi");
    }
  };

  return (
    <div>
      <h2>Tạo Đơn Hàng Test</h2>
      <form className="admin-form" onSubmit={handleSubmit}>
        <label>Tên người mua</label>
        <input name="buyer" value={formData.buyer} onChange={handleChange} required />
        
        <label>Tổng tiền</label>
        <input name="total" type="number" value={formData.total} onChange={handleChange} required />
        
        <label>Ngày giao hàng (Test case)</label>
        <input name="deliveryDate" type="date" value={formData.deliveryDate} onChange={handleChange} required />
        
        <label>Ghi chú</label>
        <textarea name="note" value={formData.note} onChange={handleChange} />
        
        <button type="submit" style={{marginTop: 10}}>Tạo Đơn</button>
      </form>
    </div>
  );
}
