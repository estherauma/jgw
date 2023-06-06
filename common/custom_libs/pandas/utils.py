from tabulate import tabulate

def count_unique(df, field):
    return df[field].nunique()


def df_aggregate_by_group(df, result_fields, group_field):
    
    columns_to_replace = result_fields
    
    df[group_field] = df[group_field].replace("", "Not specified")
    
    df[columns_to_replace] = df[columns_to_replace].replace('', None)
    
    
    aggregation_dict = {field: lambda values: values.count() for field in result_fields}
    grouped_data = df.groupby(group_field)[result_fields].agg(aggregation_dict)
    
    result = {
        "labels": grouped_data.index.values,
    }
    
    for field in result_fields:
        result[field] = grouped_data[field].values
    
    return result


def print_pandas_df_in_table_format(df, headers='keys', tablefmt='rounded_grid'):
    print(tabulate(df, headers=headers, tablefmt=tablefmt))
