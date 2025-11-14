import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
    const [data, setData] = useState({
        totalPeople: 13,
        todayPeople: 30,
        genderDistribution: { M: 14, F: 16 },
        categories: { Oferte: 4, Facturi: 7, Diverse: 19 }
    });

    useEffect(() => {
        fetch('https://exemplu.com/api/dashboard')
            .then(res => res.json())
            .then(json => setData(json))
            .catch(err => console.error(err));
    }, []);

    const genderData = [
        { name: 'Masculin', value: data.genderDistribution.M },
        { name: 'Feminin', value: data.genderDistribution.F }
    ];

    const categoriesData = [
        { name: 'Oferte', value: data.categories.Oferte },
        { name: 'Facturi', value: data.categories.Facturi },
        { name: 'Diverse', value: data.categories.Diverse }
    ];

    const genderColors = ['#3399ff', '#66d9ff'];
    const categoryColors = ['#00CFFF', '#007BFF', '#6dbdda'];

    return (
        <div style={{
            backgroundColor: '#007BFF',
            minHeight: '100vh',
            padding: '50px',
            color: 'white',
            fontFamily: 'Arial, sans-serif',
            display: 'flex',
            flexDirection: 'column',
            gap: '50px',
            overflowX: "hidden"
        }}>
            {/* Header */}
            <h1 style={{ textAlign: 'center', marginBottom: '40px' }}>Dashboard Oameni Ajutați</h1>

            {/* Statistici generale */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-around',
                gap: '20px',
                flexWrap: 'wrap',
            }}>
                <div style={{
                    backgroundColor: '#0056b3',
                    borderRadius: '10px',
                    padding: '30px 50px',
                    textAlign: 'center',
                    flex: 1,
                    minWidth: '250px',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.2)'
                }}>
                    <p style={{ margin: 0, fontWeight: 'bold' }}>Persoane ajutate până acum</p>
                    <p style={{ margin: 0, fontSize: '2rem' }}>{data.totalPeople}</p>
                </div>

                <div style={{
                    backgroundColor: '#0056b3',
                    borderRadius: '10px',
                    padding: '30px 50px',
                    textAlign: 'center',
                    flex: 1,
                    minWidth: '250px',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.2)'
                }}>
                    <p style={{ margin: 0, fontWeight: 'bold' }}>Persoane ajutate astăzi</p>
                    <p style={{ margin: 0, fontSize: '2rem' }}>{data.todayPeople}</p>
                </div>
            </div>

            {/* Grafice */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-around',
                gap: '50px',
                flexWrap: 'wrap',
            }}>


                {/* Categories Pie Chart */}
                <div style={{ backgroundColor: '#0056b3', borderRadius: '10px', padding: '20px', flex: 1, minWidth: '300px', height: '300px' }}>
                    <h3 style={{ textAlign: 'center', marginBottom: '10px' }}>Categorii</h3>
                    <ResponsiveContainer width="100%" height="80%">
                        <PieChart>
                            <Pie
                                data={categoriesData}
                                dataKey="value"
                                nameKey="name"
                                outerRadius={100}
                                label
                            >
                                {categoriesData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={categoryColors[index]} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend verticalAlign="bottom" />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
                <div style={{ textAlign: 'center', marginTop: '20vh' }}>
                    <button style={{
                        backgroundColor: '#ff4d4d',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        padding: '15px 30px',
                        fontSize: '1rem',
                        cursor: 'pointer',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.2)',
                        transition: '0.3s'
                    }}
                            onClick={() => alert('Raise a Problem clicked!')}
                    >
                        Raise a Problem
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
