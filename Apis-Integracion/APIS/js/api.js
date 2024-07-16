const API_URL_VENTAS = 'http://localhost:8000';
const API_URL_LOGISTICA = 'http://localhost:8001';
const API_URL_CLIENTES = 'http://localhost:8002';

export const generateReceipt = async (order) => {
    try {
        const response = await fetch(`${API_URL_VENTAS}/generar_boleta/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(order),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error generating receipt:', error);
        throw error; // Rethrow the error to handle it at a higher level if needed
    }
};

export const updateShipmentStatus = async (shipment) => {
    try {
        const response = await fetch(`${API_URL_LOGISTICA}/estado_envio/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(shipment),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error updating shipment status:', error);
        throw error;
    }
};

export const getCustomer = async (customerId) => {
    try {
        const response = await fetch(`${API_URL_CLIENTES}/api/cliente/${customerId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching customer:', error);
        throw error;
    }
};

export const createCustomer = async (customer) => {
    try {
        const response = await fetch(`${API_URL_VENTAS}/crear_cliente`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(customer),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error creating customer:', error);
        throw error;
    }
};
